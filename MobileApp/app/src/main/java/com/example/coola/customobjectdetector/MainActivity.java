package com.example.coola.customobjectdetector;

import android.content.Intent;
import android.graphics.Bitmap;
import android.net.Uri;
import android.os.Bundle;
import android.provider.MediaStore;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;


public class MainActivity extends AppCompatActivity {

   DetectorFunction detectorFunction;

    Button selectImage;
    ImageView imageView;

    private int REQUEST_CODE = 1;
//    private Bitmap resizedBitmap = null;
//    private Bitmap final_input_bitmap = null;



//    ------------------------Open Gallery functions-------------------------------------

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        detectorFunction = new DetectorFunction(this);

        selectImage = findViewById(R.id.selectImage);
        imageView = findViewById(R.id.Image);

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

        if(requestCode != REQUEST_CODE || resultCode != RESULT_OK )
        {
            String s = String.valueOf(REQUEST_CODE+requestCode);
            String s1 = String.valueOf(RESULT_OK+resultCode);
            Toast.makeText(this, "Image path not found :-" + s + "   "+ s1, Toast.LENGTH_SHORT).show();

        }
        else{

            try{
                Uri uri = data.getData();

                Bitmap bitmap = MediaStore.Images.Media.getBitmap(getContentResolver(),uri);
                Bitmap detectedImage = detectorFunction.processImage(bitmap,false);
                try {
                    imageView.setImageBitmap(detectedImage);
                }catch (Exception e){
                    imageView.setImageBitmap(bitmap);
                    Toast.makeText(this, "cannot decode imageView from bitmap" + e.toString(), Toast.LENGTH_SHORT).show();

                }
            }
            catch(Exception e)
            {
                Toast.makeText(this, "cannot decode imageView from bitmap" + e.toString(), Toast.LENGTH_SHORT).show();
            }


        }
    }


//    -------------------------------------******************************-------------------------------------

    void pickImage(){
        Intent intent = new Intent();
        intent.setType("image/*");
        intent.setAction(Intent.ACTION_GET_CONTENT);
        startActivityForResult(intent,REQUEST_CODE);
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


}
