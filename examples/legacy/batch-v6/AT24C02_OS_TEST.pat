// PAT File: AT24C02_TEST
// Description: AT24C02 I2C Full Test
// Generated: 2026-03-22 10:17:56
// Tool: EEPROM PAT Generator v6.0.0
// Target ATE: AdaptStar-E (EStar)

HEAD[PIN_NAME]:
  
 A0,
 A1,
 A2,
 WP,
 SCL,
 SDA;
 
END_HEAD;
TIMING timing_i2c {
    PERIOD  = 2500ns;   // 400.0 kHz
    tDRV    = 0ns;        // Drive data at period start
    tCMP    = 1250ns;    // Compare strobe at mid-period
    tPLC    = 0ns;        // Pin Low  clock edge
    tPHC    = 1250ns;    // Pin High clock edge
}

LEVEL level_5v {
    VCC  = 5.0V;
    VIH  = 3.5V;    // Input High threshold
    VIL  = 1.5V;    // Input Low  threshold
    VOH  = 2.4V;    // Output High minimum
    VOL  = 0.4V;    // Output Low  maximum
    IOL  = 3.0mA;   // Output Low  sink current
    VCLH = 6.0V;    // Clamp High
    VCLL = -0.3V;   // Clamp Low
}

@@PATTERN_DEFINE  
// OS_TEST
// A0,A1,A2,WP,SCL,SDA

OS_ALL_LOW:         000000;AC_SET 1;
                    000000;    //Hold LOW
                    000000;    //Hold LOW
                    000000;    //Hold LOW
OS_ALL_HIGH:        111111;    //OS_TEST: All pins drive HIGH
                    111111;    //Hold HIGH
                    111111;    //Hold HIGH
                    111111;    //Hold HIGH
OS_WALK1_A0:        100000;    //Walking-1: A0=HIGH, others=LOW
                    100000;    //Hold A0=HIGH
                    100000;    //Hold A0=HIGH
OS_WALK1_A1:        010000;    //Walking-1: A1=HIGH, others=LOW
                    010000;    //Hold A1=HIGH
                    010000;    //Hold A1=HIGH
OS_WALK1_A2:        001000;    //Walking-1: A2=HIGH, others=LOW
                    001000;    //Hold A2=HIGH
                    001000;    //Hold A2=HIGH
OS_WALK1_WP:        000100;    //Walking-1: WP=HIGH, others=LOW
                    000100;    //Hold WP=HIGH
                    000100;    //Hold WP=HIGH
OS_WALK1_SCL:       000010;    //Walking-1: SCL=HIGH, others=LOW
                    000010;    //Hold SCL=HIGH
                    000010;    //Hold SCL=HIGH
OS_WALK1_SDA:       000001;    //Walking-1: SDA=HIGH, others=LOW
                    000001;    //Hold SDA=HIGH
                    000001;    //Hold SDA=HIGH
OS_WALK0_A0:        011111;    //Walking-0: A0=LOW, others=HIGH
                    011111;    //Hold A0=LOW
                    011111;    //Hold A0=LOW
OS_WALK0_A1:        101111;    //Walking-0: A1=LOW, others=HIGH
                    101111;    //Hold A1=LOW
                    101111;    //Hold A1=LOW
OS_WALK0_A2:        110111;    //Walking-0: A2=LOW, others=HIGH
                    110111;    //Hold A2=LOW
                    110111;    //Hold A2=LOW
OS_WALK0_WP:        111011;    //Walking-0: WP=LOW, others=HIGH
                    111011;    //Hold WP=LOW
                    111011;    //Hold WP=LOW
OS_WALK0_SCL:       111101;    //Walking-0: SCL=LOW, others=HIGH
                    111101;    //Hold SCL=LOW
                    111101;    //Hold SCL=LOW
OS_WALK0_SDA:       111110;    //Walking-0: SDA=LOW, others=HIGH
                    111110;    //Hold SDA=LOW
                    111110;    //Hold SDA=LOW
OS_END:             000011;    //Return to IDLE
                    000011;

@@END_PATTERN_DEFINE
