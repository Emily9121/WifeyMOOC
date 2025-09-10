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
import android.util.Log;

public class WifeyUtils {
    
    private static final String TAG = "WifeyUtils";

    // Permission-requesting function
    public static void requestStoragePermission(QtActivity activity) {
        Log.d(TAG, "Requesting storage permission...");
        
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            // Android 11+ - Request All Files Access permission
            if (!Environment.isExternalStorageManager()) {
                try {
                    Intent intent = new Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION);
                    intent.addCategory("android.intent.category.DEFAULT");
                    intent.setData(Uri.parse(String.format("package:%s", activity.getApplicationContext().getPackageName())));
                    activity.startActivityForResult(intent, 101);
                    Log.d(TAG, "Requested MANAGE_APP_ALL_FILES_ACCESS_PERMISSION");
                } catch (Exception e) {
                    Log.e(TAG, "Failed to request specific app permission, trying general permission", e);
                    Intent intent = new Intent();
                    intent.setAction(Settings.ACTION_MANAGE_ALL_FILES_ACCESS_PERMISSION);
                    activity.startActivityForResult(intent, 101);
                }
            } else {
                Log.d(TAG, "Already have MANAGE_APP_ALL_FILES_ACCESS_PERMISSION");
            }
        } else {
            // Android 10 and below - Request READ_EXTERNAL_STORAGE
            String permission = "android.permission.READ_EXTERNAL_STORAGE";
            if (ActivityCompat.checkSelfPermission(activity, permission) != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(activity, new String[]{permission}, 101);
                Log.d(TAG, "Requested READ_EXTERNAL_STORAGE permission");
            } else {
                Log.d(TAG, "Already have READ_EXTERNAL_STORAGE permission");
            }
        }
    }

    // Enhanced path translator with comprehensive URI handling
    public static String getPathFromUri(Context context, String uriString) {
        try {
            Uri uri = Uri.parse(uriString);
            String path = null;
            
            Log.d(TAG, "Processing URI: " + uriString);
            Log.d(TAG, "URI scheme: " + uri.getScheme());
            Log.d(TAG, "URI authority: " + uri.getAuthority());
            
            // Handle file:// URIs
            if ("file".equalsIgnoreCase(uri.getScheme())) {
                path = uri.getPath();
                Log.d(TAG, "File URI resolved to: " + path);
            }
            
            // Handle document URIs (content:// with document structure)
            else if (DocumentsContract.isDocumentUri(context, uri)) {
                final String docId = DocumentsContract.getDocumentId(uri);
                final String authority = uri.getAuthority();
                
                Log.d(TAG, "Document URI - Authority: " + authority + ", DocId: " + docId);
                
                // External storage documents
                if ("com.android.externalstorage.documents".equals(authority)) {
                    final String[] split = docId.split(":");
                    final String type = split[0];
                    
                    if ("primary".equalsIgnoreCase(type)) {
                        if (split.length > 1) {
                            path = Environment.getExternalStorageDirectory() + "/" + split[1];
                        } else {
                            path = Environment.getExternalStorageDirectory().toString();
                        }
                        Log.d(TAG, "External storage path: " + path);
                    } else {
                        // Handle secondary storage (SD cards, etc.)
                        Log.d(TAG, "Secondary storage type: " + type);
                        path = "/storage/" + type + "/" + (split.length > 1 ? split[1] : "");
                    }
                }
                
                // Downloads provider
                else if ("com.android.providers.downloads.documents".equals(authority)) {
                    try {
                        final Uri contentUri = android.content.ContentUris.withAppendedId(
                            Uri.parse("content://downloads/public_downloads"), 
                            Long.valueOf(docId));
                        path = getDataColumn(context, contentUri, null, null);
                        Log.d(TAG, "Downloads path: " + path);
                    } catch (NumberFormatException e) {
                        Log.e(TAG, "Could not parse download document ID as long: " + docId);
                        // Try alternative approach for newer Android versions
                        if (docId.startsWith("raw:")) {
                            path = docId.replaceFirst("raw:", "");
                            Log.d(TAG, "Raw downloads path: " + path);
                        }
                    }
                }
                
                // Media provider
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
                    
                    if (contentUri != null && split.length > 1) {
                        final String selection = "_id=?";
                        final String[] selectionArgs = new String[]{split[1]};
                        path = getDataColumn(context, contentUri, selection, selectionArgs);
                        Log.d(TAG, "Media path: " + path);
                    }
                }
                
                // Google Drive and other cloud providers
                else if ("com.google.android.apps.docs.storage".equals(authority)) {
                    Log.d(TAG, "Google Drive document detected - cannot resolve to local path");
                    return uriString; // Return original URI for cloud documents
                }
            }
            
            // Handle regular content:// URIs
            else if ("content".equalsIgnoreCase(uri.getScheme())) {
                // Check if it's a Google Photos URI
                if ("com.google.android.apps.photos.content".equals(uri.getAuthority())) {
                    Log.d(TAG, "Google Photos content - cannot resolve to local path");
                    return uriString;
                }
                
                path = getDataColumn(context, uri, null, null);
                Log.d(TAG, "Content URI path: " + path);
            }
            
            // Validate the resolved path
            if (path != null && !path.isEmpty()) {
                java.io.File file = new java.io.File(path);
                if (file.exists()) {
                    Log.d(TAG, "Resolved path exists: " + path);
                    return path;
                } else {
                    Log.w(TAG, "Resolved path does not exist: " + path);
                }
            }
            
            // Final fallback
            Log.d(TAG, "Using original URI as fallback: " + uriString);
            return uriString;
            
        } catch (Exception e) {
            Log.e(TAG, "Error processing URI: " + uriString, e);
            return uriString; // Return original URI if translation fails
        }
    }

    // Helper function to get the path from a content URI using MediaStore
    private static String getDataColumn(Context context, Uri uri, String selection, String[] selectionArgs) {
        Cursor cursor = null;
        final String column = "_data";
        final String[] projection = {column};
        
        try {
            cursor = context.getContentResolver().query(uri, projection, selection, selectionArgs, null);
            if (cursor != null && cursor.moveToFirst()) {
                final int columnIndex = cursor.getColumnIndexOrThrow(column);
                String path = cursor.getString(columnIndex);
                Log.d(TAG, "getDataColumn resolved: " + path);
                return path;
            }
        } catch (Exception e) {
            Log.e(TAG, "getDataColumn failed for URI: " + uri, e);
        } finally {
            if (cursor != null) {
                cursor.close();
            }
        }
        
        Log.d(TAG, "getDataColumn returned null for URI: " + uri);
        return null;
    }
    
    // Helper method to check if external storage is available
    public static boolean isExternalStorageReadable() {
        String state = Environment.getExternalStorageState();
        return Environment.MEDIA_MOUNTED.equals(state) || Environment.MEDIA_MOUNTED_READ_ONLY.equals(state);
    }
    
    // Helper method to get common storage paths for fallback searching
    public static String[] getCommonStoragePaths() {
        return new String[] {
            Environment.getExternalStorageDirectory().getAbsolutePath(),
            Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS).getAbsolutePath(),
            "/storage/emulated/0",
            "/storage/emulated/0/Download",
            "/sdcard",
            "/sdcard/Download"
        };
    }
}
