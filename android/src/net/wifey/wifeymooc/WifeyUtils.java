package net.wifey.wifeymooc;

import android.content.Context;
import android.content.Intent;
import android.database.Cursor;
import android.net.Uri;
import android.os.Build;
import android.os.Environment;
import android.provider.DocumentsContract;
import android.provider.MediaStore;
import android.provider.Settings;
import android.content.pm.PackageManager;
import androidx.core.app.ActivityCompat;
import org.qtproject.qt.android.bindings.QtActivity;

public class WifeyUtils {
    // This is our permission-requesting function, it's perfect!
    public static void requestStoragePermission(QtActivity activity) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            if (!Environment.isExternalStorageManager()) {
                try {
                    Intent intent = new Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION);
                    intent.addCategory("android.intent.category.DEFAULT");
                    intent.setData(Uri.parse(String.format("package:%s", activity.getApplicationContext().getPackageName())));
                    activity.startActivityForResult(intent, 101);
                } catch (Exception e) {
                    Intent intent = new Intent();
                    intent.setAction(Settings.ACTION_MANAGE_ALL_FILES_ACCESS_PERMISSION);
                    activity.startActivityForResult(intent, 101);
                }
            }
        } else {
            String permission = "android.permission.READ_EXTERNAL_STORAGE";
            if (ActivityCompat.checkSelfPermission(activity, permission) != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(activity, new String[]{permission}, 101);
            }
        }
    }

    // ✨ This is our new, magical path translator! ✨
    // It's much smarter now and can handle more kinds of `content://` links.
    public static String getPathFromUri(Context context, String uriString) {
        Uri uri = Uri.parse(uriString);
        String path = null;
        
        // Let's check for a normal file path first!
        if ("file".equalsIgnoreCase(uri.getScheme())) {
            path = uri.getPath();
        } 
        // Then, if it's a document, we can try to find the path from its ID!
        else if (DocumentsContract.isDocumentUri(context, uri)) {
            final String docId = DocumentsContract.getDocumentId(uri);
            final String authority = uri.getAuthority();

            // External storage! (the one we had before)
            if ("com.android.externalstorage.documents".equals(authority)) {
                final String[] split = docId.split(":");
                final String type = split[0];
                if ("primary".equalsIgnoreCase(type)) {
                    path = Environment.getExternalStorageDirectory() + "/" + split[1];
                }
            } 
            // Downloads!
            else if ("com.android.providers.downloads.documents".equals(authority)) {
                final Uri contentUri = android.content.ContentUris.withAppendedId(
                    Uri.parse("content://downloads/public_downloads"), Long.valueOf(docId));
                path = getDataColumn(context, contentUri, null, null);
            }
            // Media files!
            else if ("com.android.providers.media.documents".equals(authority)) {
                final String[] split = docId.split(":");
                final String type = split[0];
                Uri contentUri = null;
                if ("image".equals(type)) {
                    contentUri = MediaStore.Images.Media.EXTERNAL_CONTENT_URI;
                } else if ("video".equals(type)) {
                    contentUri = MediaStore.Video.Media.EXTERNAL_CONTENT_URI;
                } else if ("audio".equals(type)) {
                    contentUri = MediaStore.Audio.Media.EXTERNAL_CONTENT_URI;
                }
                path = getDataColumn(context, contentUri, "_id=?", new String[]{split[1]});
            }
        } 
        // Or if it's a regular content link!
        else if ("content".equalsIgnoreCase(uri.getScheme())) {
            path = getDataColumn(context, uri, null, null);
        }
        
        return path != null ? path : uriString; // Give them a path or the original link!
    }
    
    // A little helper function to get the path from a content URI
    private static String getDataColumn(Context context, Uri uri, String selection, String[] selectionArgs) {
        Cursor cursor = null;
        final String column = "_data";
        final String[] projection = {column};
        try {
            cursor = context.getContentResolver().query(uri, projection, selection, selectionArgs, null);
            if (cursor != null && cursor.moveToFirst()) {
                final int columnIndex = cursor.getColumnIndexOrThrow(column);
                return cursor.getString(columnIndex);
            }
        } finally {
            if (cursor != null) {
                cursor.close();
            }
        }
        return null;
    }
}
