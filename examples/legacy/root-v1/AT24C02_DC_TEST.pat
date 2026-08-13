//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=
// PAT File: DC_TEST
// Description: DC Parameter Test
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
PATTERN DC_TEST

// Vec#    A0   A1   A2  SDA  SCL   WP   // Comment
// ------------------------------------------------
  DC_ISB_START:
   V0000    0   0   0   1   1   0   // === DC ISB Test: Standby Current ===
   V0001    0   0   0   1   1   0   // ISB: IDLE state (measure ICC)
   V0002    0   0   0   1   1   0   // ISB: IDLE state (measure ICC)
   V0003    0   0   0   1   1   0   // ISB: IDLE state (measure ICC)
   V0004    0   0   0   1   1   0   // ISB: IDLE state (measure ICC)
   V0005    0   0   0   1   1   0   // ISB: IDLE state (measure ICC)
   V0006    0   0   0   1   1   0   // ISB: IDLE state (measure ICC)
   V0007    0   0   0   1   1   0   // ISB: IDLE state (measure ICC)
   V0008    0   0   0   1   1   0   // ISB: IDLE state (measure ICC)
  DC_ISB_MEAS:
   V0009    0   0   0   1   1   0   // ISB measurement point
   V0010    0   0   0   1   1   0   // ISB: continue IDLE
   V0011    0   0   0   1   1   0   // ISB: continue IDLE
   V0012    0   0   0   1   1   0   // ISB: continue IDLE
   V0013    0   0   0   1   1   0   // ISB: continue IDLE
  DC_ICC_START:
   V0014    0   0   0   1   1   0   // === DC ICC Test: Operating Current (Read) ===
   V0015    0   0   0   1   1   0   // START Setup
   V0016    0   0   0   0   1   0   // START Condition (SDA↓)
   V0017    0   0   0   0   0   0   // START Hold
   V0018    0   0   0   1   0   0   // Write bit=1 DevAddr+R (ICC test) bit[7]
   V0019    0   0   0   1   1   0   // SCL↑ (data valid)
   V0020    0   0   0   1   0   0   // SCL↓
   V0021    0   0   0   0   0   0   // Write bit=0 DevAddr+R (ICC test) bit[6]
   V0022    0   0   0   0   1   0   // SCL↑ (data valid)
   V0023    0   0   0   0   0   0   // SCL↓
   V0024    0   0   0   1   0   0   // Write bit=1 DevAddr+R (ICC test) bit[5]
   V0025    0   0   0   1   1   0   // SCL↑ (data valid)
   V0026    0   0   0   1   0   0   // SCL↓
   V0027    0   0   0   0   0   0   // Write bit=0 DevAddr+R (ICC test) bit[4]
   V0028    0   0   0   0   1   0   // SCL↑ (data valid)
   V0029    0   0   0   0   0   0   // SCL↓
   V0030    0   0   0   0   0   0   // Write bit=0 DevAddr+R (ICC test) bit[3]
   V0031    0   0   0   0   1   0   // SCL↑ (data valid)
   V0032    0   0   0   0   0   0   // SCL↓
   V0033    0   0   0   0   0   0   // Write bit=0 DevAddr+R (ICC test) bit[2]
   V0034    0   0   0   0   1   0   // SCL↑ (data valid)
   V0035    0   0   0   0   0   0   // SCL↓
   V0036    0   0   0   0   0   0   // Write bit=0 DevAddr+R (ICC test) bit[1]
   V0037    0   0   0   0   1   0   // SCL↑ (data valid)
   V0038    0   0   0   0   0   0   // SCL↓
   V0039    0   0   0   1   0   0   // Write bit=1 DevAddr+R (ICC test) bit[0]
   V0040    0   0   0   1   1   0   // SCL↑ (data valid)
   V0041    0   0   0   1   0   0   // SCL↓
   V0042    0   0   0   Z   0   0   // ACK
   V0043    0   0   0   L   1   0   // ACK check (expect LOW)
   V0044    0   0   0   X   0   0   // SCL↓
   V0045    0   0   0   Z   0   0   // Read bit Read data (ICC meas) bit[7]
   V0046    0   0   0   X   1   0   // SCL↑ (compare=X)
   V0047    0   0   0   X   0   0   // SCL↓
   V0048    0   0   0   Z   0   0   // Read bit Read data (ICC meas) bit[6]
   V0049    0   0   0   X   1   0   // SCL↑ (compare=X)
   V0050    0   0   0   X   0   0   // SCL↓
   V0051    0   0   0   Z   0   0   // Read bit Read data (ICC meas) bit[5]
   V0052    0   0   0   X   1   0   // SCL↑ (compare=X)
   V0053    0   0   0   X   0   0   // SCL↓
   V0054    0   0   0   Z   0   0   // Read bit Read data (ICC meas) bit[4]
   V0055    0   0   0   X   1   0   // SCL↑ (compare=X)
   V0056    0   0   0   X   0   0   // SCL↓
   V0057    0   0   0   Z   0   0   // Read bit Read data (ICC meas) bit[3]
   V0058    0   0   0   X   1   0   // SCL↑ (compare=X)
   V0059    0   0   0   X   0   0   // SCL↓
   V0060    0   0   0   Z   0   0   // Read bit Read data (ICC meas) bit[2]
   V0061    0   0   0   X   1   0   // SCL↑ (compare=X)
   V0062    0   0   0   X   0   0   // SCL↓
   V0063    0   0   0   Z   0   0   // Read bit Read data (ICC meas) bit[1]
   V0064    0   0   0   X   1   0   // SCL↑ (compare=X)
   V0065    0   0   0   X   0   0   // SCL↓
   V0066    0   0   0   Z   0   0   // Read bit Read data (ICC meas) bit[0]
   V0067    0   0   0   X   1   0   // SCL↑ (compare=X)
   V0068    0   0   0   X   0   0   // SCL↓
   V0069    0   0   0   1   0   0   // NACK from master
   V0070    0   0   0   1   1   0   // NACK (SDA=HIGH)
   V0071    0   0   0   1   0   0   // SCL↓
   V0072    0   0   0   0   0   0   // STOP Setup
   V0073    0   0   0   0   1   0   // STOP (SCL↑)
   V0074    0   0   0   1   1   0   // STOP Condition (SDA↑)
   V0075    0   0   0   1   1   0   // ICC Read complete
   V0076    0   0   0   1   1   0 
  DC_ICC_W_START:
   V0077    0   0   0   1   1   0   // === DC ICC Write Test ===
   V0078    0   0   0   1   1   0   // === Byte Write: addr=0x00 data=0x55 ===
   V0079    0   0   0   1   1   0 
   V0080    0   0   0   1   1   0   // START Setup
   V0081    0   0   0   0   1   0   // START Condition (SDA↓)
   V0082    0   0   0   0   0   0   // START Hold
   V0083    0   0   0   1   0   0   // Write bit=1 DevAddr+W bit[7]
   V0084    0   0   0   1   1   0   // SCL↑ (data valid)
   V0085    0   0   0   1   0   0   // SCL↓
   V0086    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[6]
   V0087    0   0   0   0   1   0   // SCL↑ (data valid)
   V0088    0   0   0   0   0   0   // SCL↓
   V0089    0   0   0   1   0   0   // Write bit=1 DevAddr+W bit[5]
   V0090    0   0   0   1   1   0   // SCL↑ (data valid)
   V0091    0   0   0   1   0   0   // SCL↓
   V0092    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[4]
   V0093    0   0   0   0   1   0   // SCL↑ (data valid)
   V0094    0   0   0   0   0   0   // SCL↓
   V0095    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[3]
   V0096    0   0   0   0   1   0   // SCL↑ (data valid)
   V0097    0   0   0   0   0   0   // SCL↓
   V0098    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[2]
   V0099    0   0   0   0   1   0   // SCL↑ (data valid)
   V0100    0   0   0   0   0   0   // SCL↓
   V0101    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[1]
   V0102    0   0   0   0   1   0   // SCL↑ (data valid)
   V0103    0   0   0   0   0   0   // SCL↓
   V0104    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[0]
   V0105    0   0   0   0   1   0   // SCL↑ (data valid)
   V0106    0   0   0   0   0   0   // SCL↓
   V0107    0   0   0   Z   0   0   // ACK after DevAddr
   V0108    0   0   0   L   1   0   // ACK check (expect LOW)
   V0109    0   0   0   X   0   0   // SCL↓
   V0110    0   0   0   0   0   0   // Write bit=0 WordAddr bit[7]
   V0111    0   0   0   0   1   0   // SCL↑ (data valid)
   V0112    0   0   0   0   0   0   // SCL↓
   V0113    0   0   0   0   0   0   // Write bit=0 WordAddr bit[6]
   V0114    0   0   0   0   1   0   // SCL↑ (data valid)
   V0115    0   0   0   0   0   0   // SCL↓
   V0116    0   0   0   0   0   0   // Write bit=0 WordAddr bit[5]
   V0117    0   0   0   0   1   0   // SCL↑ (data valid)
   V0118    0   0   0   0   0   0   // SCL↓
   V0119    0   0   0   0   0   0   // Write bit=0 WordAddr bit[4]
   V0120    0   0   0   0   1   0   // SCL↑ (data valid)
   V0121    0   0   0   0   0   0   // SCL↓
   V0122    0   0   0   0   0   0   // Write bit=0 WordAddr bit[3]
   V0123    0   0   0   0   1   0   // SCL↑ (data valid)
   V0124    0   0   0   0   0   0   // SCL↓
   V0125    0   0   0   0   0   0   // Write bit=0 WordAddr bit[2]
   V0126    0   0   0   0   1   0   // SCL↑ (data valid)
   V0127    0   0   0   0   0   0   // SCL↓
   V0128    0   0   0   0   0   0   // Write bit=0 WordAddr bit[1]
   V0129    0   0   0   0   1   0   // SCL↑ (data valid)
   V0130    0   0   0   0   0   0   // SCL↓
   V0131    0   0   0   0   0   0   // Write bit=0 WordAddr bit[0]
   V0132    0   0   0   0   1   0   // SCL↑ (data valid)
   V0133    0   0   0   0   0   0   // SCL↓
   V0134    0   0   0   Z   0   0   // ACK after WordAddr
   V0135    0   0   0   L   1   0   // ACK check (expect LOW)
   V0136    0   0   0   X   0   0   // SCL↓
   V0137    0   0   0   0   0   0   // Write bit=0 Data bit[7]
   V0138    0   0   0   0   1   0   // SCL↑ (data valid)
   V0139    0   0   0   0   0   0   // SCL↓
   V0140    0   0   0   1   0   0   // Write bit=1 Data bit[6]
   V0141    0   0   0   1   1   0   // SCL↑ (data valid)
   V0142    0   0   0   1   0   0   // SCL↓
   V0143    0   0   0   0   0   0   // Write bit=0 Data bit[5]
   V0144    0   0   0   0   1   0   // SCL↑ (data valid)
   V0145    0   0   0   0   0   0   // SCL↓
   V0146    0   0   0   1   0   0   // Write bit=1 Data bit[4]
   V0147    0   0   0   1   1   0   // SCL↑ (data valid)
   V0148    0   0   0   1   0   0   // SCL↓
   V0149    0   0   0   0   0   0   // Write bit=0 Data bit[3]
   V0150    0   0   0   0   1   0   // SCL↑ (data valid)
   V0151    0   0   0   0   0   0   // SCL↓
   V0152    0   0   0   1   0   0   // Write bit=1 Data bit[2]
   V0153    0   0   0   1   1   0   // SCL↑ (data valid)
   V0154    0   0   0   1   0   0   // SCL↓
   V0155    0   0   0   0   0   0   // Write bit=0 Data bit[1]
   V0156    0   0   0   0   1   0   // SCL↑ (data valid)
   V0157    0   0   0   0   0   0   // SCL↓
   V0158    0   0   0   1   0   0   // Write bit=1 Data bit[0]
   V0159    0   0   0   1   1   0   // SCL↑ (data valid)
   V0160    0   0   0   1   0   0   // SCL↓
   V0161    0   0   0   Z   0   0   // ACK after Data
   V0162    0   0   0   L   1   0   // ACK check (expect LOW)
   V0163    0   0   0   X   0   0   // SCL↓
   V0164    0   0   0   0   0   0   // STOP Setup
   V0165    0   0   0   0   1   0   // STOP (SCL↑)
   V0166    0   0   0   1   1   0   // STOP Condition (SDA↑)
   V0167    0   0   0   1   1   0   // Write cycle wait (tWR)
   V0168    0   0   0   1   1   0 
   V0169    0   0   0   1   1   0 
   V0170    0   0   0   1   1   0 
   V0171    0   0   0   1   1   0 
   V0172    0   0   0   1   1   0 
   V0173    0   0   0   1   1   0 
   V0174    0   0   0   1   1   0 
   V0175    0   0   0   1   1   0 
   V0176    0   0   0   1   1   0 
  DC_VOL_START:
   V0177    0   0   0   1   1   0   // === DC VOL Test (SDA output LOW during ACK) ===
   V0178    0   0   0   1   1   0   // START Setup
   V0179    0   0   0   0   1   0   // START Condition (SDA↓)
   V0180    0   0   0   0   0   0   // START Hold
   V0181    0   0   0   1   0   0   // Write bit=1 DevAddr+W bit[7]
   V0182    0   0   0   1   1   0   // SCL↑ (data valid)
   V0183    0   0   0   1   0   0   // SCL↓
   V0184    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[6]
   V0185    0   0   0   0   1   0   // SCL↑ (data valid)
   V0186    0   0   0   0   0   0   // SCL↓
   V0187    0   0   0   1   0   0   // Write bit=1 DevAddr+W bit[5]
   V0188    0   0   0   1   1   0   // SCL↑ (data valid)
   V0189    0   0   0   1   0   0   // SCL↓
   V0190    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[4]
   V0191    0   0   0   0   1   0   // SCL↑ (data valid)
   V0192    0   0   0   0   0   0   // SCL↓
   V0193    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[3]
   V0194    0   0   0   0   1   0   // SCL↑ (data valid)
   V0195    0   0   0   0   0   0   // SCL↓
   V0196    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[2]
   V0197    0   0   0   0   1   0   // SCL↑ (data valid)
   V0198    0   0   0   0   0   0   // SCL↓
   V0199    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[1]
   V0200    0   0   0   0   1   0   // SCL↑ (data valid)
   V0201    0   0   0   0   0   0   // SCL↓
   V0202    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[0]
   V0203    0   0   0   0   1   0   // SCL↑ (data valid)
   V0204    0   0   0   0   0   0   // SCL↓
   V0205    0   0   0   Z   0   0   // *** VOL measurement point (ACK=LOW) ***
   V0206    0   0   0   L   1   0   // ACK check (expect LOW)
   V0207    0   0   0   X   0   0   // SCL↓
   V0208    0   0   0   0   0   0   // Write bit=0 WordAddr=0x00 bit[7]
   V0209    0   0   0   0   1   0   // SCL↑ (data valid)
   V0210    0   0   0   0   0   0   // SCL↓
   V0211    0   0   0   0   0   0   // Write bit=0 WordAddr=0x00 bit[6]
   V0212    0   0   0   0   1   0   // SCL↑ (data valid)
   V0213    0   0   0   0   0   0   // SCL↓
   V0214    0   0   0   0   0   0   // Write bit=0 WordAddr=0x00 bit[5]
   V0215    0   0   0   0   1   0   // SCL↑ (data valid)
   V0216    0   0   0   0   0   0   // SCL↓
   V0217    0   0   0   0   0   0   // Write bit=0 WordAddr=0x00 bit[4]
   V0218    0   0   0   0   1   0   // SCL↑ (data valid)
   V0219    0   0   0   0   0   0   // SCL↓
   V0220    0   0   0   0   0   0   // Write bit=0 WordAddr=0x00 bit[3]
   V0221    0   0   0   0   1   0   // SCL↑ (data valid)
   V0222    0   0   0   0   0   0   // SCL↓
   V0223    0   0   0   0   0   0   // Write bit=0 WordAddr=0x00 bit[2]
   V0224    0   0   0   0   1   0   // SCL↑ (data valid)
   V0225    0   0   0   0   0   0   // SCL↓
   V0226    0   0   0   0   0   0   // Write bit=0 WordAddr=0x00 bit[1]
   V0227    0   0   0   0   1   0   // SCL↑ (data valid)
   V0228    0   0   0   0   0   0   // SCL↓
   V0229    0   0   0   0   0   0   // Write bit=0 WordAddr=0x00 bit[0]
   V0230    0   0   0   0   1   0   // SCL↑ (data valid)
   V0231    0   0   0   0   0   0   // SCL↓
   V0232    0   0   0   Z   0   0   // VOL meas point 2
   V0233    0   0   0   L   1   0   // ACK check (expect LOW)
   V0234    0   0   0   X   0   0   // SCL↓
   V0235    0   0   0   0   0   0   // STOP Setup
   V0236    0   0   0   0   1   0   // STOP (SCL↑)
   V0237    0   0   0   1   1   0   // STOP Condition (SDA↑)
   V0238    0   0   0   1   1   0   // IDLE
   V0239    0   0   0   1   1   0 
  DC_VOH_START:
   V0240    0   0   0   1   1   0   // === DC VOH Test (SDA output HIGH during Read) ===
   V0241    0   0   0   1   1   0   // === Byte Write: addr=0x10 data=0xFF ===
   V0242    0   0   0   1   1   0 
   V0243    0   0   0   1   1   0   // START Setup
   V0244    0   0   0   0   1   0   // START Condition (SDA↓)
   V0245    0   0   0   0   0   0   // START Hold
   V0246    0   0   0   1   0   0   // Write bit=1 DevAddr+W bit[7]
   V0247    0   0   0   1   1   0   // SCL↑ (data valid)
   V0248    0   0   0   1   0   0   // SCL↓
   V0249    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[6]
   V0250    0   0   0   0   1   0   // SCL↑ (data valid)
   V0251    0   0   0   0   0   0   // SCL↓
   V0252    0   0   0   1   0   0   // Write bit=1 DevAddr+W bit[5]
   V0253    0   0   0   1   1   0   // SCL↑ (data valid)
   V0254    0   0   0   1   0   0   // SCL↓
   V0255    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[4]
   V0256    0   0   0   0   1   0   // SCL↑ (data valid)
   V0257    0   0   0   0   0   0   // SCL↓
   V0258    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[3]
   V0259    0   0   0   0   1   0   // SCL↑ (data valid)
   V0260    0   0   0   0   0   0   // SCL↓
   V0261    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[2]
   V0262    0   0   0   0   1   0   // SCL↑ (data valid)
   V0263    0   0   0   0   0   0   // SCL↓
   V0264    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[1]
   V0265    0   0   0   0   1   0   // SCL↑ (data valid)
   V0266    0   0   0   0   0   0   // SCL↓
   V0267    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[0]
   V0268    0   0   0   0   1   0   // SCL↑ (data valid)
   V0269    0   0   0   0   0   0   // SCL↓
   V0270    0   0   0   Z   0   0   // ACK after DevAddr
   V0271    0   0   0   L   1   0   // ACK check (expect LOW)
   V0272    0   0   0   X   0   0   // SCL↓
   V0273    0   0   0   0   0   0   // Write bit=0 WordAddr bit[7]
   V0274    0   0   0   0   1   0   // SCL↑ (data valid)
   V0275    0   0   0   0   0   0   // SCL↓
   V0276    0   0   0   0   0   0   // Write bit=0 WordAddr bit[6]
   V0277    0   0   0   0   1   0   // SCL↑ (data valid)
   V0278    0   0   0   0   0   0   // SCL↓
   V0279    0   0   0   0   0   0   // Write bit=0 WordAddr bit[5]
   V0280    0   0   0   0   1   0   // SCL↑ (data valid)
   V0281    0   0   0   0   0   0   // SCL↓
   V0282    0   0   0   1   0   0   // Write bit=1 WordAddr bit[4]
   V0283    0   0   0   1   1   0   // SCL↑ (data valid)
   V0284    0   0   0   1   0   0   // SCL↓
   V0285    0   0   0   0   0   0   // Write bit=0 WordAddr bit[3]
   V0286    0   0   0   0   1   0   // SCL↑ (data valid)
   V0287    0   0   0   0   0   0   // SCL↓
   V0288    0   0   0   0   0   0   // Write bit=0 WordAddr bit[2]
   V0289    0   0   0   0   1   0   // SCL↑ (data valid)
   V0290    0   0   0   0   0   0   // SCL↓
   V0291    0   0   0   0   0   0   // Write bit=0 WordAddr bit[1]
   V0292    0   0   0   0   1   0   // SCL↑ (data valid)
   V0293    0   0   0   0   0   0   // SCL↓
   V0294    0   0   0   0   0   0   // Write bit=0 WordAddr bit[0]
   V0295    0   0   0   0   1   0   // SCL↑ (data valid)
   V0296    0   0   0   0   0   0   // SCL↓
   V0297    0   0   0   Z   0   0   // ACK after WordAddr
   V0298    0   0   0   L   1   0   // ACK check (expect LOW)
   V0299    0   0   0   X   0   0   // SCL↓
   V0300    0   0   0   1   0   0   // Write bit=1 Data bit[7]
   V0301    0   0   0   1   1   0   // SCL↑ (data valid)
   V0302    0   0   0   1   0   0   // SCL↓
   V0303    0   0   0   1   0   0   // Write bit=1 Data bit[6]
   V0304    0   0   0   1   1   0   // SCL↑ (data valid)
   V0305    0   0   0   1   0   0   // SCL↓
   V0306    0   0   0   1   0   0   // Write bit=1 Data bit[5]
   V0307    0   0   0   1   1   0   // SCL↑ (data valid)
   V0308    0   0   0   1   0   0   // SCL↓
   V0309    0   0   0   1   0   0   // Write bit=1 Data bit[4]
   V0310    0   0   0   1   1   0   // SCL↑ (data valid)
   V0311    0   0   0   1   0   0   // SCL↓
   V0312    0   0   0   1   0   0   // Write bit=1 Data bit[3]
   V0313    0   0   0   1   1   0   // SCL↑ (data valid)
   V0314    0   0   0   1   0   0   // SCL↓
   V0315    0   0   0   1   0   0   // Write bit=1 Data bit[2]
   V0316    0   0   0   1   1   0   // SCL↑ (data valid)
   V0317    0   0   0   1   0   0   // SCL↓
   V0318    0   0   0   1   0   0   // Write bit=1 Data bit[1]
   V0319    0   0   0   1   1   0   // SCL↑ (data valid)
   V0320    0   0   0   1   0   0   // SCL↓
   V0321    0   0   0   1   0   0   // Write bit=1 Data bit[0]
   V0322    0   0   0   1   1   0   // SCL↑ (data valid)
   V0323    0   0   0   1   0   0   // SCL↓
   V0324    0   0   0   Z   0   0   // ACK after Data
   V0325    0   0   0   L   1   0   // ACK check (expect LOW)
   V0326    0   0   0   X   0   0   // SCL↓
   V0327    0   0   0   0   0   0   // STOP Setup
   V0328    0   0   0   0   1   0   // STOP (SCL↑)
   V0329    0   0   0   1   1   0   // STOP Condition (SDA↑)
   V0330    0   0   0   1   1   0   // Write cycle wait (tWR)
   V0331    0   0   0   1   1   0 
   V0332    0   0   0   1   1   0 
   V0333    0   0   0   1   1   0 
   V0334    0   0   0   1   1   0 
   V0335    0   0   0   1   1   0 
   V0336    0   0   0   1   1   0 
   V0337    0   0   0   1   1   0 
   V0338    0   0   0   1   1   0 
   V0339    0   0   0   1   1   0 
   V0340    0   0   0   1   1   0   // === Random Read: addr=0x10 ===
   V0341    0   0   0   1   1   0 
   V0342    0   0   0   1   1   0   // START Setup
   V0343    0   0   0   0   1   0   // START Condition (SDA↓)
   V0344    0   0   0   0   0   0   // START Hold
   V0345    0   0   0   1   0   0   // Write bit=1 DevAddr+W bit[7]
   V0346    0   0   0   1   1   0   // SCL↑ (data valid)
   V0347    0   0   0   1   0   0   // SCL↓
   V0348    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[6]
   V0349    0   0   0   0   1   0   // SCL↑ (data valid)
   V0350    0   0   0   0   0   0   // SCL↓
   V0351    0   0   0   1   0   0   // Write bit=1 DevAddr+W bit[5]
   V0352    0   0   0   1   1   0   // SCL↑ (data valid)
   V0353    0   0   0   1   0   0   // SCL↓
   V0354    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[4]
   V0355    0   0   0   0   1   0   // SCL↑ (data valid)
   V0356    0   0   0   0   0   0   // SCL↓
   V0357    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[3]
   V0358    0   0   0   0   1   0   // SCL↑ (data valid)
   V0359    0   0   0   0   0   0   // SCL↓
   V0360    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[2]
   V0361    0   0   0   0   1   0   // SCL↑ (data valid)
   V0362    0   0   0   0   0   0   // SCL↓
   V0363    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[1]
   V0364    0   0   0   0   1   0   // SCL↑ (data valid)
   V0365    0   0   0   0   0   0   // SCL↓
   V0366    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[0]
   V0367    0   0   0   0   1   0   // SCL↑ (data valid)
   V0368    0   0   0   0   0   0   // SCL↓
   V0369    0   0   0   Z   0   0   // ACK after DevAddr
   V0370    0   0   0   L   1   0   // ACK check (expect LOW)
   V0371    0   0   0   X   0   0   // SCL↓
   V0372    0   0   0   0   0   0   // Write bit=0 WordAddr bit[7]
   V0373    0   0   0   0   1   0   // SCL↑ (data valid)
   V0374    0   0   0   0   0   0   // SCL↓
   V0375    0   0   0   0   0   0   // Write bit=0 WordAddr bit[6]
   V0376    0   0   0   0   1   0   // SCL↑ (data valid)
   V0377    0   0   0   0   0   0   // SCL↓
   V0378    0   0   0   0   0   0   // Write bit=0 WordAddr bit[5]
   V0379    0   0   0   0   1   0   // SCL↑ (data valid)
   V0380    0   0   0   0   0   0   // SCL↓
   V0381    0   0   0   1   0   0   // Write bit=1 WordAddr bit[4]
   V0382    0   0   0   1   1   0   // SCL↑ (data valid)
   V0383    0   0   0   1   0   0   // SCL↓
   V0384    0   0   0   0   0   0   // Write bit=0 WordAddr bit[3]
   V0385    0   0   0   0   1   0   // SCL↑ (data valid)
   V0386    0   0   0   0   0   0   // SCL↓
   V0387    0   0   0   0   0   0   // Write bit=0 WordAddr bit[2]
   V0388    0   0   0   0   1   0   // SCL↑ (data valid)
   V0389    0   0   0   0   0   0   // SCL↓
   V0390    0   0   0   0   0   0   // Write bit=0 WordAddr bit[1]
   V0391    0   0   0   0   1   0   // SCL↑ (data valid)
   V0392    0   0   0   0   0   0   // SCL↓
   V0393    0   0   0   0   0   0   // Write bit=0 WordAddr bit[0]
   V0394    0   0   0   0   1   0   // SCL↑ (data valid)
   V0395    0   0   0   0   0   0   // SCL↓
   V0396    0   0   0   Z   0   0   // ACK after WordAddr
   V0397    0   0   0   L   1   0   // ACK check (expect LOW)
   V0398    0   0   0   X   0   0   // SCL↓
   V0399    0   0   0   1   0   0   // RepSTART: SDA↑
   V0400    0   0   0   1   1   0   // RepSTART: SCL↑
   V0401    0   0   0   0   1   0   // RepSTART: SDA↓
   V0402    0   0   0   0   0   0   // RepSTART: SCL↓
   V0403    0   0   0   1   0   0   // Write bit=1 DevAddr+R bit[7]
   V0404    0   0   0   1   1   0   // SCL↑ (data valid)
   V0405    0   0   0   1   0   0   // SCL↓
   V0406    0   0   0   0   0   0   // Write bit=0 DevAddr+R bit[6]
   V0407    0   0   0   0   1   0   // SCL↑ (data valid)
   V0408    0   0   0   0   0   0   // SCL↓
   V0409    0   0   0   1   0   0   // Write bit=1 DevAddr+R bit[5]
   V0410    0   0   0   1   1   0   // SCL↑ (data valid)
   V0411    0   0   0   1   0   0   // SCL↓
   V0412    0   0   0   0   0   0   // Write bit=0 DevAddr+R bit[4]
   V0413    0   0   0   0   1   0   // SCL↑ (data valid)
   V0414    0   0   0   0   0   0   // SCL↓
   V0415    0   0   0   0   0   0   // Write bit=0 DevAddr+R bit[3]
   V0416    0   0   0   0   1   0   // SCL↑ (data valid)
   V0417    0   0   0   0   0   0   // SCL↓
   V0418    0   0   0   0   0   0   // Write bit=0 DevAddr+R bit[2]
   V0419    0   0   0   0   1   0   // SCL↑ (data valid)
   V0420    0   0   0   0   0   0   // SCL↓
   V0421    0   0   0   0   0   0   // Write bit=0 DevAddr+R bit[1]
   V0422    0   0   0   0   1   0   // SCL↑ (data valid)
   V0423    0   0   0   0   0   0   // SCL↓
   V0424    0   0   0   1   0   0   // Write bit=1 DevAddr+R bit[0]
   V0425    0   0   0   1   1   0   // SCL↑ (data valid)
   V0426    0   0   0   1   0   0   // SCL↓
   V0427    0   0   0   Z   0   0   // ACK after DevAddr+R
   V0428    0   0   0   L   1   0   // ACK check (expect LOW)
   V0429    0   0   0   X   0   0   // SCL↓
   V0430    0   0   0   Z   0   0   // Read bit ReadData bit[7]
   V0431    0   0   0   H   1   0   // SCL↑ (compare=H)
   V0432    0   0   0   X   0   0   // SCL↓
   V0433    0   0   0   Z   0   0   // Read bit ReadData bit[6]
   V0434    0   0   0   H   1   0   // SCL↑ (compare=H)
   V0435    0   0   0   X   0   0   // SCL↓
   V0436    0   0   0   Z   0   0   // Read bit ReadData bit[5]
   V0437    0   0   0   H   1   0   // SCL↑ (compare=H)
   V0438    0   0   0   X   0   0   // SCL↓
   V0439    0   0   0   Z   0   0   // Read bit ReadData bit[4]
   V0440    0   0   0   H   1   0   // SCL↑ (compare=H)
   V0441    0   0   0   X   0   0   // SCL↓
   V0442    0   0   0   Z   0   0   // Read bit ReadData bit[3]
   V0443    0   0   0   H   1   0   // SCL↑ (compare=H)
   V0444    0   0   0   X   0   0   // SCL↓
   V0445    0   0   0   Z   0   0   // Read bit ReadData bit[2]
   V0446    0   0   0   H   1   0   // SCL↑ (compare=H)
   V0447    0   0   0   X   0   0   // SCL↓
   V0448    0   0   0   Z   0   0   // Read bit ReadData bit[1]
   V0449    0   0   0   H   1   0   // SCL↑ (compare=H)
   V0450    0   0   0   X   0   0   // SCL↓
   V0451    0   0   0   Z   0   0   // Read bit ReadData bit[0]
   V0452    0   0   0   H   1   0   // SCL↑ (compare=H)
   V0453    0   0   0   X   0   0   // SCL↓
   V0454    0   0   0   1   0   0   // NACK (end read)
   V0455    0   0   0   1   1   0   // NACK (SDA=HIGH)
   V0456    0   0   0   1   0   0   // SCL↓
   V0457    0   0   0   0   0   0   // STOP Setup
   V0458    0   0   0   0   1   0   // STOP (SCL↑)
   V0459    0   0   0   1   1   0   // STOP Condition (SDA↑)
  DC_VIL_VIH_START:
   V0460    0   0   0   1   1   0   // === DC Input Threshold Test (VIL/VIH) ===
   V0461    0   0   0   1   1   0   // === Byte Write: addr=0x20 data=0xAA ===
   V0462    0   0   0   1   1   0 
   V0463    0   0   0   1   1   0   // START Setup
   V0464    0   0   0   0   1   0   // START Condition (SDA↓)
   V0465    0   0   0   0   0   0   // START Hold
   V0466    0   0   0   1   0   0   // Write bit=1 DevAddr+W bit[7]
   V0467    0   0   0   1   1   0   // SCL↑ (data valid)
   V0468    0   0   0   1   0   0   // SCL↓
   V0469    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[6]
   V0470    0   0   0   0   1   0   // SCL↑ (data valid)
   V0471    0   0   0   0   0   0   // SCL↓
   V0472    0   0   0   1   0   0   // Write bit=1 DevAddr+W bit[5]
   V0473    0   0   0   1   1   0   // SCL↑ (data valid)
   V0474    0   0   0   1   0   0   // SCL↓
   V0475    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[4]
   V0476    0   0   0   0   1   0   // SCL↑ (data valid)
   V0477    0   0   0   0   0   0   // SCL↓
   V0478    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[3]
   V0479    0   0   0   0   1   0   // SCL↑ (data valid)
   V0480    0   0   0   0   0   0   // SCL↓
   V0481    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[2]
   V0482    0   0   0   0   1   0   // SCL↑ (data valid)
   V0483    0   0   0   0   0   0   // SCL↓
   V0484    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[1]
   V0485    0   0   0   0   1   0   // SCL↑ (data valid)
   V0486    0   0   0   0   0   0   // SCL↓
   V0487    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[0]
   V0488    0   0   0   0   1   0   // SCL↑ (data valid)
   V0489    0   0   0   0   0   0   // SCL↓
   V0490    0   0   0   Z   0   0   // ACK after DevAddr
   V0491    0   0   0   L   1   0   // ACK check (expect LOW)
   V0492    0   0   0   X   0   0   // SCL↓
   V0493    0   0   0   0   0   0   // Write bit=0 WordAddr bit[7]
   V0494    0   0   0   0   1   0   // SCL↑ (data valid)
   V0495    0   0   0   0   0   0   // SCL↓
   V0496    0   0   0   0   0   0   // Write bit=0 WordAddr bit[6]
   V0497    0   0   0   0   1   0   // SCL↑ (data valid)
   V0498    0   0   0   0   0   0   // SCL↓
   V0499    0   0   0   1   0   0   // Write bit=1 WordAddr bit[5]
   V0500    0   0   0   1   1   0   // SCL↑ (data valid)
   V0501    0   0   0   1   0   0   // SCL↓
   V0502    0   0   0   0   0   0   // Write bit=0 WordAddr bit[4]
   V0503    0   0   0   0   1   0   // SCL↑ (data valid)
   V0504    0   0   0   0   0   0   // SCL↓
   V0505    0   0   0   0   0   0   // Write bit=0 WordAddr bit[3]
   V0506    0   0   0   0   1   0   // SCL↑ (data valid)
   V0507    0   0   0   0   0   0   // SCL↓
   V0508    0   0   0   0   0   0   // Write bit=0 WordAddr bit[2]
   V0509    0   0   0   0   1   0   // SCL↑ (data valid)
   V0510    0   0   0   0   0   0   // SCL↓
   V0511    0   0   0   0   0   0   // Write bit=0 WordAddr bit[1]
   V0512    0   0   0   0   1   0   // SCL↑ (data valid)
   V0513    0   0   0   0   0   0   // SCL↓
   V0514    0   0   0   0   0   0   // Write bit=0 WordAddr bit[0]
   V0515    0   0   0   0   1   0   // SCL↑ (data valid)
   V0516    0   0   0   0   0   0   // SCL↓
   V0517    0   0   0   Z   0   0   // ACK after WordAddr
   V0518    0   0   0   L   1   0   // ACK check (expect LOW)
   V0519    0   0   0   X   0   0   // SCL↓
   V0520    0   0   0   1   0   0   // Write bit=1 Data bit[7]
   V0521    0   0   0   1   1   0   // SCL↑ (data valid)
   V0522    0   0   0   1   0   0   // SCL↓
   V0523    0   0   0   0   0   0   // Write bit=0 Data bit[6]
   V0524    0   0   0   0   1   0   // SCL↑ (data valid)
   V0525    0   0   0   0   0   0   // SCL↓
   V0526    0   0   0   1   0   0   // Write bit=1 Data bit[5]
   V0527    0   0   0   1   1   0   // SCL↑ (data valid)
   V0528    0   0   0   1   0   0   // SCL↓
   V0529    0   0   0   0   0   0   // Write bit=0 Data bit[4]
   V0530    0   0   0   0   1   0   // SCL↑ (data valid)
   V0531    0   0   0   0   0   0   // SCL↓
   V0532    0   0   0   1   0   0   // Write bit=1 Data bit[3]
   V0533    0   0   0   1   1   0   // SCL↑ (data valid)
   V0534    0   0   0   1   0   0   // SCL↓
   V0535    0   0   0   0   0   0   // Write bit=0 Data bit[2]
   V0536    0   0   0   0   1   0   // SCL↑ (data valid)
   V0537    0   0   0   0   0   0   // SCL↓
   V0538    0   0   0   1   0   0   // Write bit=1 Data bit[1]
   V0539    0   0   0   1   1   0   // SCL↑ (data valid)
   V0540    0   0   0   1   0   0   // SCL↓
   V0541    0   0   0   0   0   0   // Write bit=0 Data bit[0]
   V0542    0   0   0   0   1   0   // SCL↑ (data valid)
   V0543    0   0   0   0   0   0   // SCL↓
   V0544    0   0   0   Z   0   0   // ACK after Data
   V0545    0   0   0   L   1   0   // ACK check (expect LOW)
   V0546    0   0   0   X   0   0   // SCL↓
   V0547    0   0   0   0   0   0   // STOP Setup
   V0548    0   0   0   0   1   0   // STOP (SCL↑)
   V0549    0   0   0   1   1   0   // STOP Condition (SDA↑)
   V0550    0   0   0   1   1   0   // Write cycle wait (tWR)
   V0551    0   0   0   1   1   0 
   V0552    0   0   0   1   1   0 
   V0553    0   0   0   1   1   0 
   V0554    0   0   0   1   1   0 
   V0555    0   0   0   1   1   0 
   V0556    0   0   0   1   1   0 
   V0557    0   0   0   1   1   0 
   V0558    0   0   0   1   1   0 
   V0559    0   0   0   1   1   0 
   V0560    0   0   0   1   1   0   // === Random Read: addr=0x20 ===
   V0561    0   0   0   1   1   0 
   V0562    0   0   0   1   1   0   // START Setup
   V0563    0   0   0   0   1   0   // START Condition (SDA↓)
   V0564    0   0   0   0   0   0   // START Hold
   V0565    0   0   0   1   0   0   // Write bit=1 DevAddr+W bit[7]
   V0566    0   0   0   1   1   0   // SCL↑ (data valid)
   V0567    0   0   0   1   0   0   // SCL↓
   V0568    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[6]
   V0569    0   0   0   0   1   0   // SCL↑ (data valid)
   V0570    0   0   0   0   0   0   // SCL↓
   V0571    0   0   0   1   0   0   // Write bit=1 DevAddr+W bit[5]
   V0572    0   0   0   1   1   0   // SCL↑ (data valid)
   V0573    0   0   0   1   0   0   // SCL↓
   V0574    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[4]
   V0575    0   0   0   0   1   0   // SCL↑ (data valid)
   V0576    0   0   0   0   0   0   // SCL↓
   V0577    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[3]
   V0578    0   0   0   0   1   0   // SCL↑ (data valid)
   V0579    0   0   0   0   0   0   // SCL↓
   V0580    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[2]
   V0581    0   0   0   0   1   0   // SCL↑ (data valid)
   V0582    0   0   0   0   0   0   // SCL↓
   V0583    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[1]
   V0584    0   0   0   0   1   0   // SCL↑ (data valid)
   V0585    0   0   0   0   0   0   // SCL↓
   V0586    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[0]
   V0587    0   0   0   0   1   0   // SCL↑ (data valid)
   V0588    0   0   0   0   0   0   // SCL↓
   V0589    0   0   0   Z   0   0   // ACK after DevAddr
   V0590    0   0   0   L   1   0   // ACK check (expect LOW)
   V0591    0   0   0   X   0   0   // SCL↓
   V0592    0   0   0   0   0   0   // Write bit=0 WordAddr bit[7]
   V0593    0   0   0   0   1   0   // SCL↑ (data valid)
   V0594    0   0   0   0   0   0   // SCL↓
   V0595    0   0   0   0   0   0   // Write bit=0 WordAddr bit[6]
   V0596    0   0   0   0   1   0   // SCL↑ (data valid)
   V0597    0   0   0   0   0   0   // SCL↓
   V0598    0   0   0   1   0   0   // Write bit=1 WordAddr bit[5]
   V0599    0   0   0   1   1   0   // SCL↑ (data valid)
   V0600    0   0   0   1   0   0   // SCL↓
   V0601    0   0   0   0   0   0   // Write bit=0 WordAddr bit[4]
   V0602    0   0   0   0   1   0   // SCL↑ (data valid)
   V0603    0   0   0   0   0   0   // SCL↓
   V0604    0   0   0   0   0   0   // Write bit=0 WordAddr bit[3]
   V0605    0   0   0   0   1   0   // SCL↑ (data valid)
   V0606    0   0   0   0   0   0   // SCL↓
   V0607    0   0   0   0   0   0   // Write bit=0 WordAddr bit[2]
   V0608    0   0   0   0   1   0   // SCL↑ (data valid)
   V0609    0   0   0   0   0   0   // SCL↓
   V0610    0   0   0   0   0   0   // Write bit=0 WordAddr bit[1]
   V0611    0   0   0   0   1   0   // SCL↑ (data valid)
   V0612    0   0   0   0   0   0   // SCL↓
   V0613    0   0   0   0   0   0   // Write bit=0 WordAddr bit[0]
   V0614    0   0   0   0   1   0   // SCL↑ (data valid)
   V0615    0   0   0   0   0   0   // SCL↓
   V0616    0   0   0   Z   0   0   // ACK after WordAddr
   V0617    0   0   0   L   1   0   // ACK check (expect LOW)
   V0618    0   0   0   X   0   0   // SCL↓
   V0619    0   0   0   1   0   0   // RepSTART: SDA↑
   V0620    0   0   0   1   1   0   // RepSTART: SCL↑
   V0621    0   0   0   0   1   0   // RepSTART: SDA↓
   V0622    0   0   0   0   0   0   // RepSTART: SCL↓
   V0623    0   0   0   1   0   0   // Write bit=1 DevAddr+R bit[7]
   V0624    0   0   0   1   1   0   // SCL↑ (data valid)
   V0625    0   0   0   1   0   0   // SCL↓
   V0626    0   0   0   0   0   0   // Write bit=0 DevAddr+R bit[6]
   V0627    0   0   0   0   1   0   // SCL↑ (data valid)
   V0628    0   0   0   0   0   0   // SCL↓
   V0629    0   0   0   1   0   0   // Write bit=1 DevAddr+R bit[5]
   V0630    0   0   0   1   1   0   // SCL↑ (data valid)
   V0631    0   0   0   1   0   0   // SCL↓
   V0632    0   0   0   0   0   0   // Write bit=0 DevAddr+R bit[4]
   V0633    0   0   0   0   1   0   // SCL↑ (data valid)
   V0634    0   0   0   0   0   0   // SCL↓
   V0635    0   0   0   0   0   0   // Write bit=0 DevAddr+R bit[3]
   V0636    0   0   0   0   1   0   // SCL↑ (data valid)
   V0637    0   0   0   0   0   0   // SCL↓
   V0638    0   0   0   0   0   0   // Write bit=0 DevAddr+R bit[2]
   V0639    0   0   0   0   1   0   // SCL↑ (data valid)
   V0640    0   0   0   0   0   0   // SCL↓
   V0641    0   0   0   0   0   0   // Write bit=0 DevAddr+R bit[1]
   V0642    0   0   0   0   1   0   // SCL↑ (data valid)
   V0643    0   0   0   0   0   0   // SCL↓
   V0644    0   0   0   1   0   0   // Write bit=1 DevAddr+R bit[0]
   V0645    0   0   0   1   1   0   // SCL↑ (data valid)
   V0646    0   0   0   1   0   0   // SCL↓
   V0647    0   0   0   Z   0   0   // ACK after DevAddr+R
   V0648    0   0   0   L   1   0   // ACK check (expect LOW)
   V0649    0   0   0   X   0   0   // SCL↓
   V0650    0   0   0   Z   0   0   // Read bit ReadData bit[7]
   V0651    0   0   0   H   1   0   // SCL↑ (compare=H)
   V0652    0   0   0   X   0   0   // SCL↓
   V0653    0   0   0   Z   0   0   // Read bit ReadData bit[6]
   V0654    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0655    0   0   0   X   0   0   // SCL↓
   V0656    0   0   0   Z   0   0   // Read bit ReadData bit[5]
   V0657    0   0   0   H   1   0   // SCL↑ (compare=H)
   V0658    0   0   0   X   0   0   // SCL↓
   V0659    0   0   0   Z   0   0   // Read bit ReadData bit[4]
   V0660    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0661    0   0   0   X   0   0   // SCL↓
   V0662    0   0   0   Z   0   0   // Read bit ReadData bit[3]
   V0663    0   0   0   H   1   0   // SCL↑ (compare=H)
   V0664    0   0   0   X   0   0   // SCL↓
   V0665    0   0   0   Z   0   0   // Read bit ReadData bit[2]
   V0666    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0667    0   0   0   X   0   0   // SCL↓
   V0668    0   0   0   Z   0   0   // Read bit ReadData bit[1]
   V0669    0   0   0   H   1   0   // SCL↑ (compare=H)
   V0670    0   0   0   X   0   0   // SCL↓
   V0671    0   0   0   Z   0   0   // Read bit ReadData bit[0]
   V0672    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0673    0   0   0   X   0   0   // SCL↓
   V0674    0   0   0   1   0   0   // NACK (end read)
   V0675    0   0   0   1   1   0   // NACK (SDA=HIGH)
   V0676    0   0   0   1   0   0   // SCL↓
   V0677    0   0   0   0   0   0   // STOP Setup
   V0678    0   0   0   0   1   0   // STOP (SCL↑)
   V0679    0   0   0   1   1   0   // STOP Condition (SDA↑)
   V0680    0   0   0   1   1   0   // === DC Test Complete ===
   V0681    0   0   0   1   1   0 
   V0682    0   0   0   1   1   0 
   V0683    0   0   0   1   1   0 

END_PATTERN // DC_TEST
