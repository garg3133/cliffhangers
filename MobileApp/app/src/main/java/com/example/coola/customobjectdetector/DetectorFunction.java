package com.example.coola.customobjectdetector;

import android.app.Activity;
import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Matrix;
import android.graphics.Paint;
import android.graphics.RectF;
import android.widget.Toast;

import com.example.coola.customobjectdetector.detector_tflite.Classifier;
import com.example.coola.customobjectdetector.detector_tflite.TFLiteObjectDetectionAPIModel;

import java.io.IOException;
import java.util.List;

public class DetectorFunction {

//    boolean isToastMsgOn = false;
    //-----------------------------------------------------------------------------------------------
    // Configuration values for the prepackaged SSD model.
    private static final int TF_OD_API_INPUT_SIZE = 512;
    private static final boolean TF_OD_API_IS_QUANTIZED = false;
    private static final String TF_OD_API_MODEL_FILE = "road_detection.tflite";
    private static final String TF_OD_API_LABELS_FILE = "file:///android_asset/road.txt";
    //    private static final DetectorMode MODE = DetectorMode.TF_OD_API;
    private static float MINIMUM_CONFIDENCE_TF_OD_API = 0.49f;
    private Classifier detector;
    private Context context;
    //-----------------------------------------------------------------------------------------------


    public DetectorFunction(Context mContext) {
        context = mContext;
        initializeDetectionFunction();
    }

    // rotate bitmap at given angle
    private static Bitmap RotateBitmap(Bitmap source, float angle) {
        Matrix matrix = new Matrix();
        matrix.postRotate(angle);
        return Bitmap.createBitmap(source, 0, 0, source.getWidth(), source.getHeight(), matrix, true);
    }

    private void initializeDetectionFunction() {


        try {
            detector =
                    TFLiteObjectDetectionAPIModel.create(
                            context.getAssets(),
                            TF_OD_API_MODEL_FILE,
                            TF_OD_API_LABELS_FILE,
                            TF_OD_API_INPUT_SIZE,
                            TF_OD_API_IS_QUANTIZED);


        } catch (final IOException e) {
//            e.printStackTrace();
            Toast.makeText(context, "Detector could not be initialized", Toast.LENGTH_SHORT).show();

        }

    }


    public Bitmap processImage(Bitmap inputBitmap,boolean turnOnToastMsg) {

//        Bitmap inputBitmap = ((BitmapDrawable)imageView.getDrawable()).getBitmap();

        Bitmap final_input_bitmap = RotateBitmap(inputBitmap, 90);

        // resize image to model input
        Bitmap resizedBitmap = Bitmap.createScaledBitmap(inputBitmap, TF_OD_API_INPUT_SIZE, TF_OD_API_INPUT_SIZE, false);

        //Load all result from model
        final List<Classifier.Recognition> results = detector.recognizeImage(resizedBitmap);

        // load canvas, paint to overlay the result on to the image
        final Canvas canvas = new Canvas(resizedBitmap);
        float start_Paint_Location_x, start_Paint_Location_y;
        final Paint paint = new Paint();
        paint.setColor(Color.RED);
        paint.setStyle(Paint.Style.STROKE);
        paint.setStrokeWidth(2.0f);



        final Paint paint2= new Paint();
        paint2.setColor(Color.WHITE);
        paint2.setTextSize(15);
        paint2.setStyle(Paint.Style.FILL_AND_STROKE);
        paint2.setStrokeWidth(2.0f);


        StringBuffer strBuf = new StringBuffer(" ----Detector Result----\n");


        strBuf.append("\n");

        for (final Classifier.Recognition result : results) {
            final RectF location = result.getLocation();
            if (location != null && result.getConfidence() >= MINIMUM_CONFIDENCE_TF_OD_API) {


                canvas.drawRect(location, paint);
                RectF scaledLocation  = new RectF();
                scaledLocation.set(location);
                canvas.drawRect(scaledLocation, paint);
                result.setLocation(scaledLocation);

                String printText = "[" + result.getId() + "] "+ result.getTitle() + " " + String.format(", %.2f", result.getConfidence());

                //draw out the recognition label and confidence
                start_Paint_Location_x = scaledLocation.left ;
                start_Paint_Location_y = scaledLocation.top + 16;
                canvas.drawText(printText, start_Paint_Location_x, start_Paint_Location_y, paint2);

                strBuf.append(printText + "\n");


            }
        }

        if (turnOnToastMsg) {
            showMessage(strBuf.toString());
        }

        return resizedBitmap;

    }

    // Toast message display
    public void showMessage(String msg) {
        ((Activity)context).runOnUiThread(
                () -> {
                    Toast.makeText(context, msg, Toast.LENGTH_SHORT).show();
                });
    }


}
