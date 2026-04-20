#include <WiFi.h>
#include <HTTPClient.h>
#include "esp_camera.h"
#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"

// WiFi credentials
const char* ssid = "NHA TRO HANH PHUC";
const char* password = "13681368";

// Server API endpoint
const char* serverUrl = "http://192.168.1.10:5000//api/frame/CAM001";

// Camera pins
#define PWDN_GPIO_NUM  32
#define RESET_GPIO_NUM -1
#define XCLK_GPIO_NUM  0
#define SIOD_GPIO_NUM  26
#define SIOC_GPIO_NUM  27
#define Y9_GPIO_NUM    35
#define Y8_GPIO_NUM    34
#define Y7_GPIO_NUM    39
#define Y6_GPIO_NUM    36
#define Y5_GPIO_NUM    21
#define Y4_GPIO_NUM    19
#define Y3_GPIO_NUM    18
#define Y2_GPIO_NUM    5
#define VSYNC_GPIO_NUM 25
#define HREF_GPIO_NUM  23
#define PCLK_GPIO_NUM  22

// Performance settings
#define FRAME_SIZE_PRESET FRAMESIZE_HVGA  // 480x320 - Cân bằng tốt
#define JPEG_QUALITY 20  // 10-63, cao hơn = file nhỏ hơn nhưng chất lượng kém
#define SEND_INTERVAL 50  // 50ms = 20 FPS target

HTTPClient http;
WiFiClient client;
unsigned long frameCount = 0;
unsigned long lastFpsTime = 0;

void setup() {
  Serial.begin(115200);
  
  // Disable brownout detector
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0);
  
  Serial.println("\nESP32-CAM High Performance Mode");
  
  if (!initCamera()) {
    Serial.println("Camera init failed!");
    ESP.restart();
  }
  
  connectWiFi();
  
  // Pre-configure HTTP client
  http.setReuse(true);  // Keep connection alive
  http.setTimeout(2000);
  
  Serial.println("Ready! Starting stream...");
  lastFpsTime = millis();
}

void loop() {
  sendFrameFast();
  
  // FPS counter
  frameCount++;
  if (millis() - lastFpsTime >= 1000) {
    Serial.printf("FPS: %lu, Free heap: %d\n", frameCount, ESP.getFreeHeap());
    frameCount = 0;
    lastFpsTime = millis();
  }
}

bool initCamera() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  
  // High speed clock
  config.xclk_freq_hz = 20000000;
  
  // Optimal frame size for speed
  config.frame_size = FRAME_SIZE_PRESET;
  config.pixel_format = PIXFORMAT_JPEG;
  config.grab_mode = CAMERA_GRAB_LATEST;  // Skip old frames
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality = JPEG_QUALITY;
  config.fb_count = 2;  // Double buffering
  
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed: 0x%x\n", err);
    return false;
  }
  
  // Sensor optimizations
  sensor_t * s = esp_camera_sensor_get();
  
  // Disable unnecessary features for speed
  s->set_brightness(s, 0);
  s->set_contrast(s, 0);
  s->set_saturation(s, 0);
  s->set_special_effect(s, 0);
  s->set_whitebal(s, 1);
  s->set_awb_gain(s, 1);
  s->set_wb_mode(s, 0);
  s->set_exposure_ctrl(s, 1);
  s->set_aec2(s, 0);
  s->set_ae_level(s, 0);
  s->set_aec_value(s, 300);
  s->set_gain_ctrl(s, 1);
  s->set_agc_gain(s, 0);
  s->set_gainceiling(s, (gainceiling_t)0);
  s->set_bpc(s, 0);
  s->set_wpc(s, 1);
  s->set_raw_gma(s, 1);
  s->set_lenc(s, 1);
  s->set_hmirror(s, 0);
  s->set_vflip(s, 0);
  s->set_dcw(s, 1);
  s->set_colorbar(s, 0);
  
  return true;
}

void connectWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false);  // Disable WiFi sleep for better performance
  WiFi.begin(ssid, password);
  
  Serial.print("Connecting");
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nConnected!");
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());
    Serial.print("Signal: ");
    Serial.println(WiFi.RSSI());
  } else {
    Serial.println("\nFailed!");
    ESP.restart();
  }
}

void sendFrameFast() {
  camera_fb_t *fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Capture failed");
    esp_camera_fb_return(fb);
    return;
  }
  
  // Skip if frame is too large (network congestion)
  if (fb->len > 50000) {
    esp_camera_fb_return(fb);
    return;
  }
  
  http.begin(client, serverUrl);
  http.addHeader("Content-Type", "image/jpeg");
  http.addHeader("Content-Length", String(fb->len));
  
  int httpCode = http.POST((uint8_t*)fb->buf, fb->len);
  
  // Only log errors
  if (httpCode < 0) {
    Serial.printf("E:%d ", httpCode);
  }
  
  http.end();
  esp_camera_fb_return(fb);
}