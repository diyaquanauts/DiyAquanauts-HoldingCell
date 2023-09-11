import argparse
from fileGuiOperations import fileSelection
import fnmatch
import ntpath
import os
from os import walk
import sys
import cv2
import numpy as np
from matplotlib import pyplot as plt

class CnnPreProcessing:
    @staticmethod
    def CreateClosedEdgeImage(sourceImg):
        srcEdges = cv2.Canny(sourceImg, 50, 150, apertureSize=3)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
        closed = cv2.morphologyEx(srcEdges, cv2.MORPH_CLOSE, kernel)
        return closed

    @staticmethod
    def CropImageFromBoundingFeature(sourceImg, boundingBuffer=1):
        closedVersion = CnnPreProcessing.CreateClosedEdgeImage(sourceImg)
        (cnts, _) = cv2.findContours(closedVersion.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        bestBoudningBox = [-1, -1, -1, -1]

        for c in cnts:
            x, y, w, h = cv2.boundingRect(c)
            if bestBoudningBox[0] < 0:
                bestBoudningBox = [x, y, x + w, y + h]
            else:
                if x < bestBoudningBox[0]:
                    bestBoudningBox[0] = x
                if y < bestBoudningBox[1]:
                    bestBoudningBox[1] = y
                if x + w > bestBoudningBox[2]:
                    bestBoudningBox[2] = x + w
                if y + h > bestBoudningBox[3]:
                    bestBoudningBox[3] = y + h

        try:
            x = x - boundingBuffer
            y = y - boundingBuffer
            w = w + 2 * boundingBuffer
            h = h + 2 * boundingBuffer
            sourceImg = sourceImg[y:y + h, x:x + w]
        except Exception as inst:
            print(inst)
            print("Unable to create bounding buffer!")

        return sourceImg

    @staticmethod
    def CreateColorQuantizedImage(sourceImg):
        Z = sourceImg.reshape((-1, 3))
        Z = np.float32(Z)
        kCluster = 2
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        ret, label, center = cv2.kmeans(Z, kCluster, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        center = np.uint8(center)
        res = center[label.flatten()]
        colorQuantized = res.reshape((sourceImg.shape))
        return colorQuantized

    @staticmethod
    def SaveImage(outputFile, imageData):
        try:
            cv2.imwrite(outputFile, imageData)
        except:
            print("Unable to write '" + outputFile + "'!")

    @staticmethod
    def CreateConvolutionProfile(sourceFile, outputDir):
        baseFileName = ntpath.basename(sourceFile)
        baseFilePath = os.path.join(outputDir, baseFileName)
        originalImage = cv2.imread(sourceFile)
        colorQuantized = CnnPreProcessing.CreateColorQuantizedImage(originalImage)
        colorQuantizedCrop = CnnPreProcessing.CropImageFromBoundingFeature(colorQuantized)
        CnnPreProcessing.SaveImage(baseFilePath + ".CQ.png", colorQuantizedCrop)
        Gaussian = cv2.GaussianBlur(originalImage, (7, 7), 0)
        GaussianCrop = CnnPreProcessing.CropImageFromBoundingFeature(Gaussian)
        CnnPreProcessing.SaveImage(baseFilePath + ".Gaussian.png", GaussianCrop)
        Median = cv2.medianBlur(originalImage, 5)
        MedianCrop = Median.copy()
        MedianCrop = CnnPreProcessing.CropImageFromBoundingFeature(MedianCrop)
        CnnPreProcessing.SaveImage(baseFilePath + ".Median.png", MedianCrop)
        Bilateral = cv2.bilateralFilter(originalImage, 9, 75, 75)
        BilateralCrop = CnnPreProcessing.CropImageFromBoundingFeature(Bilateral)
        CnnPreProcessing.SaveImage(baseFilePath + ".Bilateral.png", BilateralCrop)
        cropOriginal = originalImage.copy()
        cropOriginal = CnnPreProcessing.CropImageFromBoundingFeature(cropOriginal, boundingBuffer=5)
        CnnPreProcessing.SaveImage(baseFilePath + ".Cropped.png", cropOriginal)
        orgEdges = cv2.Canny(originalImage, 50, 150, apertureSize=3)
        orgEdgeCrop = CnnPreProcessing.CropImageFromBoundingFeature(orgEdges)
        CnnPreProcessing.SaveImage(baseFilePath + ".CannyEdge.png", orgEdgeCrop)
        cqEdges = cv2.Canny(colorQuantized, 50, 150, apertureSize=3)
        cqEdgesCrop = CnnPreProcessing.CropImageFromBoundingFeature(cqEdges)
        CnnPreProcessing.SaveImage(baseFilePath + ".CQEdge.png", cqEdgesCrop)
        biEdges = cv2.Canny(Bilateral, 50, 150, apertureSize=3)
        biEdgesCrop = CnnPreProcessing.CropImageFromBoundingFeature(biEdges)
        CnnPreProcessing.SaveImage(baseFilePath + ".BiEdge.png", biEdgesCrop)
        gausEdges = cv2.Canny(Gaussian, 50, 150, apertureSize=3)
        gausEdgesCrop = CnnPreProcessing.CropImageFromBoundingFeature(gausEdges)
        CnnPreProcessing.SaveImage(baseFilePath + ".GaussEdge.png", gausEdgesCrop)
        medEdges = cv2.Canny(Median, 50, 150, apertureSize=3)
        medEdgesCrop = CnnPreProcessing.CropImageFromBoundingFeature(medEdges)
        CnnPreProcessing.SaveImage(baseFilePath + ".MedianEdge.png", medEdgesCrop)

    @staticmethod
    def isImageFile(filename, extensions=['.jpg', '.jpeg', '.gif', '.png']):
        return any(filename.endswith(e) for e in extensions)

    @staticmethod
    def processPath(path):
        if os.path.isdir(path):
            outputDir = os.path.join(path, "Convolutions")
            try:
                os.mkdir(outputDir)
            except:
                print("Output directory may already exist...")
            for root, dirs, files in os.walk(path, topdown=False):
                for name in files:
                    path = os.path.join(root, name)
                    if CnnPreProcessing.isImageFile(path):
                        print(path)
                        try:
                            CnnPreProcessing.CreateConvolutionProfile(path, outputDir)
                        except:
                            print("Unable to create full convolution profile!")
        elif os.path.isfile(path):
            CnnPreProcessing.CreateConvolutionProfile(path, "./")
        else:
            print("This is a special socket, FIFO, or device file!")

if __name__ == "__main__":

# Example usage:
    fileOps = fileSelection()

    path = fileOps.selectFile("png")

    if path:
        CnnPreProcessing.processPath(path)
