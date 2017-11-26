package com.moodmetric.demoapp;

import android.app.Activity;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothGatt;
import android.bluetooth.BluetoothGattCallback;
import android.bluetooth.BluetoothGattCharacteristic;
import android.bluetooth.BluetoothGattDescriptor;
import android.bluetooth.BluetoothGattService;
import android.bluetooth.BluetoothManager;
import android.bluetooth.BluetoothProfile;
import android.bluetooth.le.BluetoothLeScanner;
import android.bluetooth.le.ScanCallback;
import android.bluetooth.le.ScanFilter;
import android.bluetooth.le.ScanRecord;
import android.bluetooth.le.ScanResult;
import android.bluetooth.le.ScanSettings;
import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.os.ParcelUuid;
import android.util.Log;
import android.view.View;
import android.widget.ScrollView;
import android.widget.TextView;

import java.net.URL;
import java.net.URLConnection;

import java.util.List;
import java.util.UUID;
import java.util.ArrayList;

public class DemoActivity extends Activity {

    private static final int REQUEST_ENABLE_BT = 1;
    private static final UUID mmServiceUUID =
            UUID.fromString("dd499b70-e4cd-4988-a923-a7aab7283f8e");
    private static final UUID streamingCharacteristicUUID =
            UUID.fromString("a0956420-9bd2-11e4-bd06-0800200c9a66");
    // Defined by the BLE standard
    private static final UUID clientCharacteristicConfigurationUUID =
            UUID.fromString("00002902-0000-1000-8000-00805F9B34FB");

    private BluetoothAdapter bluetoothAdapter;
    private BluetoothLeScanner scanner;
    private BluetoothGatt bleGatt;
    private boolean scanning;
    private TextView logView;
    private ScrollView scrollView;

    private List<ScanFilter> filters;
    private ScanSettings settings;

    private final BluetoothGattCallback gattCallback = new BluetoothGattCallback() {
        @Override
        public void onConnectionStateChange(final BluetoothGatt gatt, int status, int newState) {
            if (newState == BluetoothProfile.STATE_CONNECTED) {
                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        log("connection established, discovering services");
                        // Once we have connection start BLE service discovery
                        gatt.discoverServices();
                    }
                });
            }
        }

        @Override
        public void onServicesDiscovered(final BluetoothGatt gatt, int status) {
            runOnUiThread(
                    new Runnable() {
                        @Override
                        public void run() {
                            enableStreamingNotification(gatt);
                        }
                    });
        }

        private void enableStreamingNotification(BluetoothGatt gatt) {
            log("services discovered, enabling notifications");
            // Get the MM service
            BluetoothGattService mmService = gatt.getService(mmServiceUUID);
            // Get the streaming characteristic
            BluetoothGattCharacteristic streamingCharacteristic =
                    mmService.getCharacteristic(streamingCharacteristicUUID);
            // Enable notifications on the streaming characteristic
            gatt.setCharacteristicNotification(streamingCharacteristic, true);
            // For some reason the above does not tell the ring that it should
            // start sending notifications, so we have to do it explicitly
            BluetoothGattDescriptor cccDescriptor =
                    streamingCharacteristic.getDescriptor(clientCharacteristicConfigurationUUID);
            cccDescriptor.setValue(BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE);
            gatt.writeDescriptor(cccDescriptor);
        }

        @Override
        public void onCharacteristicChanged(
                BluetoothGatt gatt, BluetoothGattCharacteristic characteristic) {
            byte[] payload = characteristic.getValue();
            // Decode payload
            int status = payload[0] & 0xff;
            int mm = payload[1] & 0xff;
            // Instant EDA value is in payload bytes 2 and 3 in big-endian format
            int instant = ((payload[2] & 0xff) << 8) | (payload[3] & 0xff);
            // Acceleration in x, y and z directions
            int ax = payload[4] & 0xff;
            int ay = payload[5] & 0xff;
            int az = payload[6] & 0xff;
            // Acceleration magnitude
            double a = Math.sqrt(ax*ax + ay*ay + az*az);
            String s=HttpRequest.sendGet("http://10.100.0.74/ring-input/"+mm, "");
            Log.e("H", s);
            log("st:%02x\tmm:%d\teda:%d\ta:%.1f", status, mm, instant, a);
        }
    };

    private final ScanCallback scanCallback =
            new ScanCallback() {
                @Override
                public void onScanResult(int callbackType, ScanResult result) {
                    Log.e("G", "0.0");
                    super.onScanResult(callbackType, result);
                    final byte[] scanRecord = result.getScanRecord().getBytes();
                    final BluetoothDevice device = result.getDevice();
                    final int rssi = result.getRssi();
                    Log.e("G", "0.1"+device+rssi);
                    log("found ring %s, rssi: %d", device.getAddress(), rssi);
                    stopScanning();
                    runOnUiThread(
                            new Runnable() {
                                @Override
                                public void run() {
                                    log("connecting with %s", device.getAddress());
                                    // Establish a connection with the ring.
                                    bleGatt = device.connectGatt(DemoActivity.this, false, gattCallback);
                                }
                            });
                }
            };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_demo);
        logView = (TextView)findViewById(R.id.logView);
        scrollView = (ScrollView)findViewById(R.id.scrollView);

        // Get the bluetooth manager from Android
        final BluetoothManager bluetoothManager =
                (BluetoothManager)getSystemService(Context.BLUETOOTH_SERVICE);
        if (bluetoothManager == null) {
            log("bluetooth service not available");
            return;
        }
        // Get a reference to the bluetooth adapter of the device
        bluetoothAdapter = bluetoothManager.getAdapter();
        if (bluetoothAdapter == null) {
            log("bluetooth not supported");
            return;
        }
        // Check that bluetooth is enabled. If not, ask the user to enable it.
        if (!bluetoothAdapter.isEnabled()) {
            Intent enableBtIntent = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
            startActivityForResult(enableBtIntent, REQUEST_ENABLE_BT);
            return;
        }
        // If bluetooth was enabled start scanning for rings.
        scanner = bluetoothAdapter.getBluetoothLeScanner();
        settings = new ScanSettings.Builder()
                .setScanMode(ScanSettings.SCAN_MODE_LOW_LATENCY)
                .build();
        startScanning();
    }

    // Called after user has allowed or rejected our request to enable bluetooth
    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == REQUEST_ENABLE_BT) {
            if (resultCode == RESULT_OK) {
                startScanning();
            } else {
                log("bluetooth not enabled");
            }
        }
    }

    private void startScanning() {
        if (scanning) return;
        scanning = true;
        log("scanning for rings");
        Log.e("F","0.0");
        // Start scanning for devices that support the Moodmetric service
        ScanFilter filter = new ScanFilter.Builder()
                .setServiceUuid(ParcelUuid.fromString("dd499b70-e4cd-4988-a923-a7aab7283f8e"))
                .build();
        Log.e("F","0.1");
        filters = new ArrayList<ScanFilter>();
        filters.add(filter);
        Log.e("F","0.2");

//        scanner.startScan( scanCallback);
        scanner.startScan(filters, settings, scanCallback);
        Log.e("F","0,3");
//        bluetoothAdapter.startLeScan(new UUID[] { mmServiceUUID }, scanCallback);
    }

    private void stopScanning() {
        if (!scanning) return;
        scanning = false;
        log("scanning stopped");
        scanner.stopScan(scanCallback);
//        bluetoothAdapter.stopLeScan(scanCallback);
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (scanning) stopScanning();
        if (bleGatt != null) {
            bleGatt.close();
        }
    }

    private void log(final String fmt, final Object... args) {
        // Updates to the UI should be done from the UI thread
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                logView.append(String.format(fmt+"\n",args));
                scrollView.fullScroll(View.FOCUS_DOWN);
            }
        });
    }
}
