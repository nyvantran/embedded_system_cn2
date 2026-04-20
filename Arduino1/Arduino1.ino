#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// ==================== CẤU HÌNH ====================
// Thông tin WiFi
const char* ssid = "NHA TRO HANH PHUC";
const char* password = "13681368";

// Cấu hình I2C cho ESP32-C3
#define I2C_SDA 8
#define I2C_SCL 9

// Địa chỉ I2C của LCD (thường là 0x27 hoặc 0x3F)
#define LCD_ADDRESS 0x27
#define LCD_COLUMNS 20
#define LCD_ROWS 4

// API endpoint - thay bằng API của bạn
const char* apiEndpoint = "http://192.168.1.10:5000//api/count/CAMM001";

// Thời gian cập nhật (ms)
const unsigned long updateInterval = 1000;  // 10 giây

// Thời gian chuyển trang LCD (ms)
const unsigned long pageInterval = 3000;  // 3 giây mỗi trang

// ==================== KHỞI TẠO ====================
LiquidCrystal_I2C lcd(LCD_ADDRESS, LCD_COLUMNS, LCD_ROWS);
unsigned long lastUpdate = 0;
unsigned long lastPageChange = 0;

// Lưu trữ dữ liệu từ API
struct DataItem {
  String key;
  String value;
};

DataItem dataItems[20];  // Tối đa 20 thuộc tính
int dataCount = 0;
int currentPage = 0;

void setup() {
  // Khởi động Serial
  Serial.begin(115200);
  delay(100);
  // Khởi động I2C với chân tùy chỉnh
  Wire.begin(I2C_SDA, I2C_SCL);

  // Khởi động LCD
  lcd.init();
  lcd.backlight();
  lcd.clear();

  // Hiển thị thông báo khởi động
  displayCentered(0, "=== ESP32-C3 ===");
  displayCentered(1, "Connecting WiFi");
  displayCentered(2, "Please wait...");

  Serial.println();
  Serial.print("Dang ket noi toi: ");
  Serial.println(ssid);

  // Kết nối WiFi
  WiFi.begin(ssid, password);
  WiFi.setTxPower(WIFI_POWER_8_5dBm);



  int dotCount = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    lcd.setCursor(dotCount % 20, 3);
    lcd.print(".");
    dotCount++;
  }

  Serial.println("\nDa ket noi WiFi!");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());

  // Hiển thị kết nối thành công
  lcd.clear();
  displayCentered(0, "WiFi Connected!");
  displayCentered(1, "IP Address:");
  displayCentered(2, WiFi.localIP().toString());

  delay(2000);

  // Lấy dữ liệu lần đầu
  fetchAPIData();
}

void loop() {
  // Kiểm tra kết nối WiFi
  if (WiFi.status() != WL_CONNECTED) {
    lcd.clear();
    displayCentered(0, "WiFi Lost!");
    displayCentered(1, "Reconnecting...");
    WiFi.reconnect();
    delay(5000);
    return;
  }

  // Cập nhật dữ liệu từ API theo chu kỳ
  if (millis() - lastUpdate >= updateInterval) {
    fetchAPIData();
    lastUpdate = millis();
  }

  // Chuyển trang hiển thị nếu có nhiều dữ liệu
  if (dataCount > 4 && millis() - lastPageChange >= pageInterval) {
    currentPage++;
    int totalPages = (dataCount + 3) / 4;  // Làm tròn lên
    if (currentPage >= totalPages) {
      currentPage = 0;
    }
    displayCurrentPage();
    lastPageChange = millis();
  }

  delay(100);
}

// ==================== HÀM LẤY DỮ LIỆU TỪ API ====================
void fetchAPIData() {
  Serial.println("\n========== FETCHING API ==========");

  // Hiển thị đang tải
  lcd.setCursor(19, 0);
  lcd.print("*");

  HTTPClient http;
  http.begin(apiEndpoint);
  http.setTimeout(10000);

  int httpCode = http.GET();

  if (httpCode > 0) {
    Serial.printf("HTTP Code: %d\n", httpCode);

    if (httpCode == HTTP_CODE_OK) {
      String payload = http.getString();
      Serial.println("Response:");
      Serial.println(payload);

      // Parse JSON và lấy tất cả thuộc tính trong "data"
      parseDataObject(payload);

      // Hiển thị trang đầu tiên
      currentPage = 0;
      displayCurrentPage();
      lastPageChange = millis();

    } else {
      displayError("HTTP Error: " + String(httpCode));
    }
  } else {
    Serial.printf("HTTP Error: %s\n", http.errorToString(httpCode).c_str());
    displayError("Connection Failed");
  }

  http.end();

  lcd.setCursor(19, 0);
  lcd.print(" ");
}

// ==================== PARSE TẤT CẢ THUỘC TÍNH TRONG "data" ====================
void parseDataObject(String json) {
  // Tạo JsonDocument đủ lớn
  DynamicJsonDocument doc(2048);

  DeserializationError error = deserializeJson(doc, json);

  if (error) {
    Serial.print("JSON Parse Error: ");
    Serial.println(error.c_str());
    displayError("JSON Parse Error");
    return;
  }

  // Reset dữ liệu cũ
  dataCount = 0;

  // Kiểm tra xem có object "data" không
  if (!doc.containsKey("data")) {
    Serial.println("Khong tim thay 'data' trong JSON");
    displayError("No 'data' found");
    return;
  }

  // Lấy object "data"
  JsonObject dataObj = doc["data"].as<JsonObject>();

  Serial.println("\n=== CAC THUOC TINH TRONG 'data' ===");

  // Duyệt qua tất cả các thuộc tính trong "data"
  for (JsonPair kv : dataObj) {
    if (dataCount >= 20) break;  // Giới hạn 20 thuộc tính

    String key = kv.key().c_str();
    String value;

    // Xử lý các kiểu dữ liệu khác nhau
    if (kv.value().is<int>()) {
      value = String(kv.value().as<int>());
    } else if (kv.value().is<float>()) {
      value = String(kv.value().as<float>(), 2);
    } else if (kv.value().is<bool>()) {
      value = kv.value().as<bool>() ? "true" : "false";
    } else if (kv.value().is<const char*>()) {
      value = kv.value().as<String>();
    } else if (kv.value().isNull()) {
      value = "null";
    } else {
      // Với object hoặc array, chuyển thành string
      serializeJson(kv.value(), value);
    }

    // Lưu vào mảng
    dataItems[dataCount].key = key;
    dataItems[dataCount].value = value;

    Serial.printf("%d. %s : %s\n", dataCount + 1, key.c_str(), value.c_str());

    dataCount++;
  }

  Serial.printf("\nTong cong: %d thuoc tinh\n", dataCount);
  Serial.println("=====================================");
}

// ==================== HIỂN THỊ TRANG HIỆN TẠI ====================
void displayCurrentPage() {
  lcd.clear();

  if (dataCount == 0) {
    displayCentered(1, "No Data");
    return;
  }

  int totalPages = (dataCount + 3) / 4;
  int startIndex = currentPage * 4;

  // Hiển thị 4 dòng (hoặc ít hơn nếu không đủ dữ liệu)
  for (int row = 0; row < 4; row++) {
    int dataIndex = startIndex + row;

    if (dataIndex < dataCount) {
      displayDataLine(row, dataItems[dataIndex].key, dataItems[dataIndex].value);
    }
  }

  // Hiển thị số trang ở góc phải dòng cuối (nếu có nhiều trang)
  if (totalPages > 1) {
    lcd.setCursor(16, 3);
    lcd.print(String(currentPage + 1) + "/" + String(totalPages));
  }

  Serial.printf("Hien thi trang %d/%d\n", currentPage + 1, totalPages);
}

// ==================== HIỂN THỊ MỘT DÒNG DỮ LIỆU ====================
void displayDataLine(int row, String key, String value) {
  // Format: "key : value"
  // LCD có 20 cột
  // Dành tối đa 8 ký tự cho key, 3 cho " : ", còn lại cho value

  lcd.setCursor(0, row);

  // Cắt key nếu quá dài
  String displayKey = key;
  if (displayKey.length() > 8) {
    displayKey = displayKey.substring(0, 8);
  }

  // Cắt value nếu quá dài (dành 8 ký tự)
  String displayValue = value;
  if (displayValue.length() > 8) {
    displayValue = displayValue.substring(0, 8);
  }

  // Tạo chuỗi hiển thị với padding
  String line = padRight(displayKey, 8) + " : " + displayValue;

  // Đảm bảo không vượt quá 20 ký tự
  if (line.length() > 20) {
    line = line.substring(0, 20);
  }

  lcd.print(line);
}

// ==================== HÀM HỖ TRỢ ====================

// Thêm khoảng trắng vào bên phải để đạt độ dài mong muốn
String padRight(String str, int length) {
  while (str.length() < length) {
    str += " ";
  }
  return str;
}

// Hiển thị text căn giữa
void displayCentered(int row, String text) {
  int startCol = (LCD_COLUMNS - text.length()) / 2;
  if (startCol < 0) startCol = 0;

  lcd.setCursor(0, row);
  lcd.print("                    ");  // Clear dòng
  lcd.setCursor(startCol, row);
  lcd.print(text.substring(0, LCD_COLUMNS));
}

// Hiển thị lỗi
void displayError(String errorMsg) {
  lcd.clear();
  displayCentered(0, "=== ERROR ===");
  displayCentered(1, errorMsg);
  displayCentered(3, "Retry soon...");

  Serial.println("ERROR: " + errorMsg);
}

// ==================== QUÉT ĐỊA CHỈ I2C ====================
void scanI2C() {
  Serial.println("\nScanning I2C...");
  byte count = 0;

  for (byte addr = 1; addr < 127; addr++) {
    Wire.beginTransmission(addr);
    if (Wire.endTransmission() == 0) {
      Serial.print("Found: 0x");
      if (addr < 16) Serial.print("0");
      Serial.println(addr, HEX);
      count++;
    }
  }

  Serial.print("Found ");
  Serial.print(count);
  Serial.println(" device(s)");
}