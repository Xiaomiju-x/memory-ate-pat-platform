//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=
// PAT File: OS_TEST
// Description: Open/Short Continuity Test
// Device: AT24C02 (2Kbit I2C EEPROM)
// Generated: 2026-03-16 09:18:35
// Tool: AT24C02 PAT Generator v1.0
// Target ATE: AdaptStar-E (EStar)
//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=

// SIGNAL_GROUP: A0, A1, A2, SDA, SCL, WP
// Pin Mapping:
//   A0  -> DUT Pin 1 (Address Input)
//   A1  -> DUT Pin 2 (Address Input)
//   A2  -> DUT Pin 3 (Address Input)
//   SDA -> DUT Pin 5 (Serial Data I/O)
//   SCL -> DUT Pin 6 (Serial Clock)
//   WP  -> DUT Pin 7 (Write Protect)
//   VCC -> DPS Channel (Pin 8)
//   GND -> DPS Ground  (Pin 4)

// Vector States:
//   0 = Drive Low    1 = Drive High
//   L = Expect Low   H = Expect High
//   Z = Hi-Z         X = Don't Care
// TIMING CONFIGURATION
// Period: 2500ns (400.0kHz)
// I2C Clock: 400kHz (Standard/Fast Mode)
PATTERN OS_TEST

// Vec#    A0   A1   A2  SDA  SCL   WP   // Comment
// ------------------------------------------------
  OS_ALL_LOW:
   V0000    0   0   0   0   0   0   // OS_TEST: All pins drive LOW
   V0001    0   0   0   0   0   0   // Hold LOW
   V0002    0   0   0   0   0   0   // Hold LOW
   V0003    0   0   0   0   0   0   // Hold LOW
  OS_ALL_HIGH:
   V0004    1   1   1   1   1   1   // OS_TEST: All pins drive HIGH
   V0005    1   1   1   1   1   1   // Hold HIGH
   V0006    1   1   1   1   1   1   // Hold HIGH
   V0007    1   1   1   1   1   1   // Hold HIGH
  OS_WALK1_A0:
   V0008    1   0   0   0   0   0   // Walking-1: A0=HIGH, others=LOW
   V0009    1   0   0   0   0   0   // Hold A0=HIGH
   V0010    1   0   0   0   0   0   // Hold A0=HIGH
  OS_WALK1_A1:
   V0011    0   1   0   0   0   0   // Walking-1: A1=HIGH, others=LOW
   V0012    0   1   0   0   0   0   // Hold A1=HIGH
   V0013    0   1   0   0   0   0   // Hold A1=HIGH
  OS_WALK1_A2:
   V0014    0   0   1   0   0   0   // Walking-1: A2=HIGH, others=LOW
   V0015    0   0   1   0   0   0   // Hold A2=HIGH
   V0016    0   0   1   0   0   0   // Hold A2=HIGH
  OS_WALK1_SDA:
   V0017    0   0   0   1   0   0   // Walking-1: SDA=HIGH, others=LOW
   V0018    0   0   0   1   0   0   // Hold SDA=HIGH
   V0019    0   0   0   1   0   0   // Hold SDA=HIGH
  OS_WALK1_SCL:
   V0020    0   0   0   0   1   0   // Walking-1: SCL=HIGH, others=LOW
   V0021    0   0   0   0   1   0   // Hold SCL=HIGH
   V0022    0   0   0   0   1   0   // Hold SCL=HIGH
  OS_WALK1_WP:
   V0023    0   0   0   0   0   1   // Walking-1: WP=HIGH, others=LOW
   V0024    0   0   0   0   0   1   // Hold WP=HIGH
   V0025    0   0   0   0   0   1   // Hold WP=HIGH
  OS_WALK0_A0:
   V0026    0   1   1   1   1   1   // Walking-0: A0=LOW, others=HIGH
   V0027    0   1   1   1   1   1   // Hold A0=LOW
   V0028    0   1   1   1   1   1   // Hold A0=LOW
  OS_WALK0_A1:
   V0029    1   0   1   1   1   1   // Walking-0: A1=LOW, others=HIGH
   V0030    1   0   1   1   1   1   // Hold A1=LOW
   V0031    1   0   1   1   1   1   // Hold A1=LOW
  OS_WALK0_A2:
   V0032    1   1   0   1   1   1   // Walking-0: A2=LOW, others=HIGH
   V0033    1   1   0   1   1   1   // Hold A2=LOW
   V0034    1   1   0   1   1   1   // Hold A2=LOW
  OS_WALK0_SDA:
   V0035    1   1   1   0   1   1   // Walking-0: SDA=LOW, others=HIGH
   V0036    1   1   1   0   1   1   // Hold SDA=LOW
   V0037    1   1   1   0   1   1   // Hold SDA=LOW
  OS_WALK0_SCL:
   V0038    1   1   1   1   0   1   // Walking-0: SCL=LOW, others=HIGH
   V0039    1   1   1   1   0   1   // Hold SCL=LOW
   V0040    1   1   1   1   0   1   // Hold SCL=LOW
  OS_WALK0_WP:
   V0041    1   1   1   1   1   0   // Walking-0: WP=LOW, others=HIGH
   V0042    1   1   1   1   1   0   // Hold WP=LOW
   V0043    1   1   1   1   1   0   // Hold WP=LOW
  OS_END:
   V0044    0   0   0   1   1   0   // Return to IDLE
   V0045    0   0   0   1   1   0   // IDLE

END_PATTERN // OS_TEST
