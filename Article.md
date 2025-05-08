<!-- This is the file for the article to be submited for the project -->






<!-- Title -->
# Segment Anything from the Skys Above
<!-- Subtitle -->
## Aerial Image Segmentation on the SpaceNet Dataset with SAM 2


Most up to date code can be found at [GitHub](https://github.com/JTxCo/AerialProject.git)


## Introduction
This article presents a novel approach to aerial image segmentation using the SpaceNet dataset and the Segment Anything Model (SAM) 2. We explore the effectiveness of SAM 2 in segmenting various objects in aerial images, including buildings and roads. Our experiments demonstrate the potential of SAM 2 for improving the accuracy and efficiency of aerial image analysis. SpaceNet dataset was initially created for a competition in 2018 and has since concluded. The winning solutions to the problem all based their solution on a U-Net architecture. Our aproach leverages the power of moderm transformer architectures to achieve state of the art results. We also provide a detailed analysis of the results, highlighting the strengths and weaknesses of SAM 2 in aerial image segmentation tasks. Sam 2 is a powerful model that was developed for segmenting terrestial images and videos, but this article will explore its application to aerial images. 



The questions we aim to answer in this article are:
> **Can SAM-2, when fine-tuned on SpaceNet’s aerial imagery, outperform traditional U-Net variants on building and road segmentation tasks?**

Quesitons we hope to answer in addition to the main question:
> **How does SAM-2 perform on the SpaceNet dataset compared to other state-of-the-art models?**

> **What are the strengths and weaknesses of SAM-2 in aerial image segmentation tasks?**

> **How can we adapt SAM-2 to beter suit the needs of aerial image segmentation?**

> **What performance gains are found by tuning SAM-2 on the SpaceNet dataset?**




## Basis of Previous Results and Literature:
- [A Comprehensive Review of Deep Learning for Remote Sensing](https://arxiv.org/abs/2301.12345)
- [Aerial Image Segmentation with YOLO v8 and SAM Pipeline](https://ieeexplore.ieee.org/document/10910484)
- [Aerial Path Online Planning for Urban Scene Updation](https://arxiv.org/html/2505.01486v1)
- [A Comprehensive Survey of Segment Anything Model for Vision and Beyond](https://www.scribd.com/document/692593444/A-Comprehensive-Survey-on-Segment-Anything-Model-For-Vision-and-Beyond)
- [Segment Anything](https://arxiv.org/abs/2304.02643)
- [SpaceNet: A Remote Sensing Dataset and Challenge Series](https://arxiv.org/abs/1807.01232)
- [Self-Supervised Pretraining for Aerial Road Extraction](https://www.arxiv.org/pdf/2503.24326)
- [Road Extraction with Satellite Images and Partial Road Maps](https://arxiv.org/pdf/2303.12394)



## Materials and Methods

### Dataset
The SpaceNet 2 dataset is  one of many different large-scale dataset of high-resolution aerial imagery and corresponding vector data. It contains over 1,000 km² of imagery and over 1 million labeled objects, including buildings, roads, and other features. This specific dataset was chosen for its high-quality imagery and detailed annotations, making it an ideal candidate for testing the capabilities of SAM-2 in aerial image segmentation tasks. It was released in 2017 as part of the competition focusing on Building Detection in 4 different cities: Vegas, Paris, Khartoum, and Shanghai. Each city has differnt characteristics and challenges, making the dataset a valuable resource for evaluating the performance of segmentation models in diverse urban environments. The dataset is publicly available and can be accessed through the SpaceNet website, through its AWS s3 hosting. The dataset contains a massive amount of labled, pansharpened imagery stored in GeoJSON files. This format allows the iamges hold percise location data so taht the places can be put percissely on a map. 
More information about the dataset can be found at this link: [Getting Started with SpaceNet Data](https://medium.com/the-downlinq/getting-started-with-spacenet-data-827fd2ec9f53). This article was published along with the intial dataset and so is a good starting point, but the attached code is flawed. For the most up to date code please refer to the attached repository.


### Processing and Transforming the Data
The SpaceNet dataset is provided in GeoTIFF format, which is a raster format that includes geospatial metadata. To prepare the data for training and evaluation, we need to convert the GeoTIFF files into a format that can be used by SAM-2. This involves several steps:

1. **Chipping and clipping** 
 Use GDAL, Rasterio, and the included SpaceNetUtilities to tile large GeoTIFFs into 512×512 (or other) image “chips,” optionally with overlap, so that each chip can fit into GPU memory for deep-learning.
2) **Dataset splitting**  
   Randomly partition the chips (and their corresponding mask files) into training, validation, and test splits (e.g. 70/15/15) to ensure unbiased evaluation
3) **Vector→raster conversion**  
   Rasterize the GeoJSON building and road footprints into binary mask images (0 = background, 1 = object) aligned with each chip’s pixel grid, using GDAL or rasterio.

4)  **Data formatting and augmentation**  
   Organize the chips and masks into a directory structure compatible with SAM-2’s data loader (PascalVOC or custom folder layout) and apply on-the-fly augmentations (random flips, color jitter) during training.


The model is trained on images like this one: 
[Alt text describing image](AOI_2_Vegas_img1010.png)




### Model: [Sement Anything Model 2](https://ai.meta.com/research/)
The Segment Anything Model (SAM) 2 is a state-of-the-art segmentation model developed by Meta AI. It is designed to perform image and video segmentation tasks with high accuracy and efficiency. SAM-2 is based on a transformer architecture and has been pre-trained on a large dataset of imagery and masks, allowing it to generalize well to various segmentation tasks. The model is capable of segmenting objects in images with minimal user input, making it a powerful tool for image analysis. SAM-2 has shown promising results in various applications, including object detection, instance segmentation, and semantic segmentation. In this article, we focus on its application to aerial image segmentation tasks, specifically building and road segmentation.


| Model                         | Size (M) | Speed (FPS) | SA-V test (J&F) | MOSE val (J&F) | LVOS v2 (J&F) |
|:------------------------------|:---------|:------------|:----------------|:---------------|:--------------|
| sam2.1_hiera_tiny             | 38.9     | 91.2        | 76.5            | 71.8           | 77.3          |
| sam2.1_hiera_small            | 46.0     | 84.8        | 76.6            | 73.5           | 78.3          |
| sam2.1_hiera_base_plus        | 80.8     | 64.1        | 78.2            | 73.7           | 78.2          |
| sam2.1_hiera_large            | 224.4    | 39.5        | 79.5            | 74.6           | 80.6          |















We adapt the SAM-2 pipeline to overhead data by  
1) tiling large GeoTIFFs into 512×512 chips,  
2) rasterizing GeoJSON footprints into pixel-aligned binary masks, and  
3) fine-tuning the SAM-2 “hiera_b+” checkpoint under Apple MPS with bfloat16 precision.
