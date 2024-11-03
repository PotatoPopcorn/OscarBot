#define VER_MAJ 2
#define VER_MIN 0
#define VER_HOT 1

#define ENA 11
#define ENB 10
#define IN1 13
#define IN2 12
#define IN3 8
#define IN4 9

#define SIDE_LEFT 'L'
#define SIDE_RIGHT 'R'
#define SIDE_UNKNOWN 'U'

#define CMD_LEN 32

#define LEFT_MIN 1020
#define RIGHT_MIN 650
#define RIGHT_MAX 700
char cmd[CMD_LEN];

int counter = 0;
unsigned char convres;

void clear_cmd() {
  memset(cmd, 0, CMD_LEN);
}

bool cmp_cmd(char* needle) {
  return memcmp(cmd, needle, 3) == 0;
}

void set_pins(char pin, char offset, char input) {
  char res = bitRead(input, offset);
  if(res == 1) {
    digitalWrite(pin, HIGH);
  } else {
    digitalWrite(pin, LOW);
  }
}

bool convert_digit(char digit, unsigned char* out) {
    if (digit >= 0x30 && digit <= 0x39) {
        *out += digit - 0x30;
        return true;
    } else if (digit >= 'A' && digit <= 'F') {
        *out += digit - 'A' + 10;
        return true;
    } else if (digit >= 'a' && digit <= 'f') {
        *out += digit - 'a' + 10;
        return true;
    }
    return false;
}

bool convert_byte(char digits[], unsigned char* out) {
    *out = 0;
    if(!convert_digit(digits[0], out)) {
        return false;
    }
    *out *= 16;
    if (!convert_digit(digits[1], out)) {
        return false;
    }
    return true;
}

char get_side() {
  char result = SIDE_UNKNOWN;
  int sample = 0;
  for (int i = 0; i < 4; ++i) {
    sample = analogRead(A0);
    if (result == SIDE_UNKNOWN && sample >= LEFT_MIN) {
      result = SIDE_LEFT;
    } else if (result == SIDE_LEFT && sample >= LEFT_MIN) {
      // Do Nothing, we have the correct side and the sample matches
    } else if (result == SIDE_LEFT && sample < LEFT_MIN) {
      return SIDE_UNKNOWN;
    } else if (result == SIDE_UNKNOWN && sample >= RIGHT_MIN && sample <= RIGHT_MAX) {
      result = SIDE_RIGHT;
    } else if (result == SIDE_RIGHT && sample >= RIGHT_MIN && sample <= RIGHT_MAX) {
      // Do Nothing, we have the correct side and the sample matches
    } else if (result == SIDE_RIGHT && (sample < RIGHT_MIN || sample > RIGHT_MAX)) {
      return SIDE_UNKNOWN;
    } else {
      return SIDE_UNKNOWN;
    }
  }
  return result;
}

void handle_init() {
  Serial.write("INI");
  Serial.write(VER_MAJ);
  Serial.write(VER_MIN);
  Serial.write(VER_HOT);
  Serial.write(get_side());
  Serial.write("\n");
}

void handle_halt() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
  analogWrite(ENA, 0);
  analogWrite(ENB, 0);
}

void set_upper_pins(char* cmd) {
  convert_byte(cmd + 3, &convres);
  set_pins(IN1, 0, convres);
  set_pins(IN2, 1, convres);
  set_pins(IN3, 2, convres);
  set_pins(IN4, 3, convres);
  convert_byte(cmd + 5, &convres);
  analogWrite(ENA, convres);
  convert_byte(cmd + 7, &convres);
  analogWrite(ENB, convres);
}

void setup() {
  Serial.begin(115200);
  pinMode(ENA, OUTPUT);
  pinMode(ENB, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  Serial.println("Started");
}

void loop() {
  //Serial.println(analogRead(A0));
  clear_cmd();
  if(Serial.available() > 0) {
    Serial.readBytesUntil('\n', cmd, CMD_LEN);
  }
  if(cmp_cmd("INI")) {
    handle_init();
  } else if (cmp_cmd("HAL")) {
    handle_halt();
  } else if (cmp_cmd("CDU")) {
    set_upper_pins(cmd);
  } else if (cmp_cmd("IDU")) {
    unsigned short wait_time = 0;
    set_upper_pins(cmd);
    convert_byte(cmd + 9, &convres);
    wait_time = convres * 256;
    convert_byte(cmd + 11, &convres);
    wait_time += convres;
    Serial.println(wait_time);
    delay(wait_time);
    handle_halt();
  }
}