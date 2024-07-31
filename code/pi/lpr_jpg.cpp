/* test code */

#include <ultimateALPR-SDK-API-PUBLIC.h>
#include <unistd.h>
#include "/home/pi/lpr/ultimateALPR/samples/c++/alpr_utils.h"

//#include <raspicam/raspicam.h>
//#include <opencv2/imgproc.hpp>

#include <ctime>
#include <fstream>
#include <iostream>
#include <stdio.h>
#include <stdlib.h> 
#include <string.h>
#include <signal.h>
#include <errno.h>
#include <fcntl.h> 
#include <sys/stat.h> 
#include <sys/types.h> 
#include <stdio.h> 

using namespace std;

#define ASSET_MGR_PARAM() 

#define IMG_WIDTH 1648
#define IMG_HEIGHT 1232

void err_exit(char *buf) {
    fprintf(stderr, "%s\n", buf);
    exit(1);
}

volatile sig_atomic_t stop;
void inthand(int signum) {
    stop = 1;
}

/* Entry point */

int main(int argc, char *argv[])
{
	signal(SIGINT, inthand);
	
	// local variables
	UltAlprSdkResult result(0, "OK", "{}");
	std::string assetsFolder;
	bool isParallelDeliveryEnabled = false;
	bool isRectificationEnabled = false;
	int width, height;

	std::string ramdisk = "/var/ramdisk"; 
	std::string pathFileImage1, pathFileImage2;
	std::string tmp;
	int img_num, i;
	FILE * fp;

	// Open file to save results
	tmp = ramdisk + "/lpr_data.txt";
	fp = fopen(tmp.c_str(),"w");
	if (fp == NULL)
		printf("!!!!! Error: Failed to open LPR result output file\n");


	assetsFolder = "/home/pi/lpr/ultimateALPR/assets";

	// configuration for ANPR deep learning engine
	static const char* __jsonConfig =
	"{"
	"\"debug_level\": \"error\","
	"\"debug_write_input_image_enabled\": false,"
	"\"debug_internal_data_path\": \".\","
	""
	"\"license_token_file\": \"/home/pi/lpr/ultimateALPR/token\","
	"\"num_threads\": -1,"
	"\"gpgpu_enabled\": true,"
	""
	"\"detect_roi\": [0, 0, 0, 0],"  // ignore top third of image for lpr
	"\"detect_minscore\": 0.1,"
	""
	"\"pyramidal_search_enabled\": false,"
	"\"pyramidal_search_sensitivity\": 0.28,"
	"\"pyramidal_search_minscore\": 0.5,"
	"\"pyramidal_search_min_image_size_inpixels\": 800,"
	""
	"\"recogn_minscore\": 0.3,"
	"\"recogn_score_type\": \"min\""
	"";

	// update JSON config
	std::string jsonConfig = __jsonConfig;
	jsonConfig += std::string(",\"assets_folder\": \"") + assetsFolder + std::string("\"");
	jsonConfig += std::string(",\"recogn_rectify_enabled\": ") + (isRectificationEnabled ? "true" : "false");
	jsonConfig += "}"; // end-of-config

	// init Alpr
	result = UltAlprSdkEngine::init(ASSET_MGR_PARAM() jsonConfig.c_str(), nullptr);
	AlprFile fileImage;

	// Continuously process images from files 
	for (img_num=0;img_num<10000;img_num++) { 

		// Get image from file
		tmp = std::to_string(img_num);
		pathFileImage1 = ramdisk + "/img_" + std::string(5-tmp.length(),'0') + tmp + ".jpg";
		tmp = std::to_string(img_num + 1);
		pathFileImage2 = ramdisk + "/img_" + std::string(5-tmp.length(),'0') + tmp + ".jpg";

		while (access(pathFileImage2.c_str(), F_OK ) == -1 ) {}  // wait for next file
		alprDecodeFile(pathFileImage1, fileImage);

		// recognize/process and output result to console
		result = UltAlprSdkEngine::process(fileImage.type, fileImage.uncompressedData, fileImage.width, fileImage.height);

		// output result to console and file
		const std::string& json_ = result.json();
		if (json_.length() > 50) {
			//printf("Results: %s\n", json_.c_str());
			fprintf(fp, "%s\n", json_.c_str());
			fflush(fp);
		}


		if (stop) break;
	}

	printf("\nExit ...\n");
	// de-init
	result = UltAlprSdkEngine::deInit();

	fclose(fp);

	return 0;
}
