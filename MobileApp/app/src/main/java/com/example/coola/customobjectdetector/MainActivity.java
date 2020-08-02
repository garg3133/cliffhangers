package com.example.coola.sih2020;

import android.content.Intent;
import android.graphics.Bitmap;
import android.net.Uri;
import android.os.Bundle;
import android.provider.MediaStore;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import im.delight.android.location.SimpleLocation;


public class MainActivity extends AppCompatActivity {

   DetectorFunction detectorFunction;

    Button selectImage;
    ImageView imageView;
    TextView displayResult;

    private int REQUEST_CODE = 1;
//    private Bitmap resizedBitmap = null;
//    private Bitmap final_input_bitmap = null;

    private SimpleLocation location;
    private static final int CAMERA_PIC_REQUEST = 1337;



//    ------------------------Open Gallery functions-------------------------------------

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);



        // construct a new instance of SimpleLocation
        location = new SimpleLocation(this);

        // if we can't access the location yet
        if (!location.hasLocationEnabled()) {
            // ask the user to enable location access
            SimpleLocation.openSettings(this);
        }

        detectorFunction = new DetectorFunction(this,location);


        selectImage = findViewById(R.id.selectImage);
        imageView = findViewById(R.id.Image);
        displayResult = findViewById(R.id.details);


        selectImage.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {

                pickImage();
            }
        });
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);

//        double latitude = location.getLatitude();
//        double longitude = location.getLongitude();
//

        if(requestCode != REQUEST_CODE || resultCode != RESULT_OK )
        {
            if (requestCode == CAMERA_PIC_REQUEST) {
                if (resultCode == RESULT_OK) {
//                    tv.setText("Got picture!");
                    Bitmap imageData = (Bitmap) data.getExtras().get("data");

                    processBitamp(imageData);
                } else if (resultCode == RESULT_CANCELED){
                    showMessage("try again");
                }
            }
            else {

                String s = String.valueOf(REQUEST_CODE + requestCode);
                String s1 = String.valueOf(RESULT_OK + resultCode);
                Toast.makeText(this, "Image path not found :-" + s + "   " + s1, Toast.LENGTH_SHORT).show();
            }
        }
        else{

            try{
                Uri uri = data.getData();

                Bitmap bitmap = MediaStore.Images.Media.getBitmap(getContentResolver(),uri);

                processBitamp(bitmap);
            }
            catch(Exception e)
            {
                Toast.makeText(this, "cannot decode imageView from bitmap" + e.toString(), Toast.LENGTH_SHORT).show();
            }


        }

//        updateLocationTextView();

    }


//    -------------------------------------******************************-------------------------------------

    void pickImage(){
        Intent intent = new Intent();
        intent.setType("image/*");
        intent.setAction(Intent.ACTION_GET_CONTENT);
        startActivityForResult(intent,REQUEST_CODE);
    }

    public void ClickPhoto(View view) {
        Intent takePictureIntent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
        startActivityForResult(takePictureIntent, CAMERA_PIC_REQUEST);
    }

    public void processBitamp(Bitmap bitmap){

        Report report = detectorFunction.processImage(bitmap,false);

        Bitmap detectedImage = report.getDetectedImage();

        displayResult.setText(report.getResultInfo());


        try {
            imageView.setImageBitmap(detectedImage);
        }catch (Exception e){
            imageView.setImageBitmap(bitmap);
            Toast.makeText(this, "cannot decode imageView from bitmap" + e.toString(), Toast.LENGTH_SHORT).show();

        }
    }


    // Toast message display
    public void showMessage(String msg) {
        runOnUiThread(
                () -> {
                    Toast.makeText(this, msg, Toast.LENGTH_SHORT).show();
                });
    }


    // Which detection model to use: by default uses Tensorflow Object Detection API frozen
    // checkpoints.
    private enum DetectorMode {
        TF_OD_API
    }


    @Override
    protected void onResume() {
        super.onResume();

        // make the device update its location
        location.beginUpdates();

        // ...
    }

    @Override
    protected void onPause() {
        // stop location updates (saves battery)
        location.endUpdates();

        // ...

        super.onPause();
    }


    public void updateLocationTextView(){
//        double latitude = location.getLatitude();
//        double longitude = location.getLongitude();

//        StringBuffer str = new StringBuffer("");
//        str.append("Latitude :-" + latitude +"\n");
//        str.append("Longitude :-" + longitude + "\n");


    }

}
