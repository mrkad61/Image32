#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <ESP32Servo.h>

// --- Pin Tanımları ---
#define TRIG_PIN 14
#define ECHO_PIN 13
#define SERVO_PIN 12

// --- LCD Ayarları (I2C Adresi 0x27 olabilir, ekranın arkasındaki modüle göre değişebilir) ---
LiquidCrystal_I2C lcd(0x27, 16, 2);

// --- Servo Nesnesi ---
Servo myServo;

// --- Zaman ve Mesafe ---
unsigned long lastMeasureTime = 0;
const unsigned long measureInterval = 100; // ms
float distanceCM = 0;

// --- Seri Veri ---
String serialBuffer = "";

void setup() {
  Serial.begin(115200);

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  myServo.setPeriodHertz(50);
  myServo.attach(SERVO_PIN, 500, 2400); // SG90 mikro-saniye aralığı
  myServo.write(90);
  // LCD başlat
  Wire.begin(21, 22); // ESP32 I2C pinleri
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("Mesafe Sistemi");
  delay(1000);
  lcd.clear();
}

void loop() {
  unsigned long now = millis();

  // --- Mesafe ölç ---
  if (now - lastMeasureTime >= measureInterval) {
    distanceCM = measureDistance();
    showOnLCD(distanceCM);
    lastMeasureTime = now;
  }

  // --- Seri porttan servo komutu al ---
  readSerialAngle();
}

// --- HC-SR04 Mesafe Ölçüm ---
float measureDistance() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH, 20000); // timeout 20ms
  float distance = duration * 0.0343 / 2;
  return (distance > 400 || duration == 0) ? -1 : distance;
}

// --- LCD'de Göster ---
void showOnLCD(float cm) {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Mesafe:");

  lcd.setCursor(0, 1);
  if (cm < 0) {
    lcd.print("Yok");
  } else {
    lcd.print(cm, 1);
    lcd.print(" cm");
  }
}

String input = "";

void readSerialAngle() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      int angle = input.toInt();             // '\n' gelince sayı olarak çevir
      angle = constrain(angle, 0, 180);      // Güvenli aralık
      myServo.write(angle);                 // Servo açı gönder
      input = "";                           // Buffer temizle
    } else {
      input += c;                           // Buffer’a ekle
    }
  }
}
