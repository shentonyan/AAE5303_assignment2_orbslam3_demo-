/**
* This file is part of ORB-SLAM3
*
* Modified to support CompressedImage messages
*/

#include<iostream>
#include<algorithm>
#include<fstream>
#include<chrono>

#include<ros/ros.h>
#include <cv_bridge/cv_bridge.h>
#include <sensor_msgs/CompressedImage.h>

#include<opencv2/core/core.hpp>
#include<opencv2/imgcodecs.hpp>

#include"../../../include/System.h"

using namespace std;

class ImageGrabber
{
public:
    ImageGrabber(ORB_SLAM3::System* pSLAM):mpSLAM(pSLAM){}

    void GrabCompressedImage(const sensor_msgs::CompressedImageConstPtr& msg);

    ORB_SLAM3::System* mpSLAM;
};

int main(int argc, char **argv)
{
    ros::init(argc, argv, "Mono");
    ros::start();

    if(argc != 3)
    {
        cerr << endl << "Usage: rosrun ORB_SLAM3 Mono_Compressed path_to_vocabulary path_to_settings" << endl;        
        ros::shutdown();
        return 1;
    }    

    // Create SLAM system. It initializes all system threads and gets ready to process frames.
    // bUseViewer=false: Disable Pangolin when no X11 (e.g. Docker/WSL) to avoid "Failed to open X display"
    ORB_SLAM3::System SLAM(argv[1],argv[2],ORB_SLAM3::System::MONOCULAR,false);

    ImageGrabber igb(&SLAM);

    ros::NodeHandle nodeHandler;
    ros::Subscriber sub = nodeHandler.subscribe("/camera/image_raw/compressed", 1, &ImageGrabber::GrabCompressedImage,&igb);

    ros::spin();

    // Stop all threads
    SLAM.Shutdown();

    // Save full-frame trajectory (required for course evaluation / leaderboard)
    SLAM.SaveTrajectoryTUM("CameraTrajectory.txt");

    // Optional: save keyframe trajectory
    SLAM.SaveKeyFrameTrajectoryTUM("KeyFrameTrajectory.txt");

    ros::shutdown();

    return 0;
}

void ImageGrabber::GrabCompressedImage(const sensor_msgs::CompressedImageConstPtr& msg)
{
    try
    {
        // Decode compressed image
        cv::Mat image = cv::imdecode(cv::Mat(msg->data), cv::IMREAD_COLOR);
        
        if(image.empty())
        {
            ROS_ERROR("Failed to decode compressed image");
            return;
        }

        // Convert to grayscale if needed (ORB-SLAM3 works with grayscale)
        // cv::Mat gray;
        // cv::cvtColor(image, gray, cv::COLOR_BGR2GRAY);
        
        double timestamp = msg->header.stamp.toSec();
        mpSLAM->TrackMonocular(image, timestamp);
    }
    catch (cv::Exception& e)
    {
        ROS_ERROR("OpenCV exception: %s", e.what());
        return;
    }
}


