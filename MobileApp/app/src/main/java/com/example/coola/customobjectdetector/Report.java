package com.example.coola.sih2020;

import android.graphics.Bitmap;

public class Report {
    private String resultInfo;
    private Bitmap detectedImage;

    public String getResultInfo() {
        return resultInfo;
    }

    public void setResultInfo(String resultInfo) {
        this.resultInfo = resultInfo;
    }

    public Bitmap getDetectedImage() {
        return detectedImage;
    }

    public void setDetectedImage(Bitmap detectedImage) {
        this.detectedImage = detectedImage;
    }

    public Report(String resultInfo, Bitmap detectedImage) {

        this.resultInfo = resultInfo;
        this.detectedImage = detectedImage;
    }
}
