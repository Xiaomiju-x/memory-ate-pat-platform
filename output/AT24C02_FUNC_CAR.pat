// PAT File: FUNC_CAR
// Description: Current Address Read
// Generated: 2026-03-25 19:58:57
// Tool: EEPROM PAT Generator v8.0.0
// Target ATE: AdaptStar-E (EStar)

HEAD[PIN_NAME]:
  
 A0,
 A1,
 A2,
 WP,
 SCL,
 SDA;
 
END_HEAD;
@@PATTERN_DEFINE  
// FUNC_CAR
// A0,A1,A2,WP,SCL,SDA

start:              000011;AC_SET 1;

                    000011;    //=== Byte Write: addr=0x10 data=0xCA ===
                    000011;

                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold

                    000001;    //Write bit=1 DevAddr+W bit[7]
                    000011;    //SCL↑ (data valid)
                    000011;    //SCL high hold
                    000001;    //SCL↓

                    000000;    //Write bit=0 DevAddr+W bit[6]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000001;    //Write bit=1 DevAddr+W bit[5]
                    000011;    //SCL↑ (data valid)
                    000011;    //SCL high hold
                    000001;    //SCL↓

                    000000;    //Write bit=0 DevAddr+W bit[4]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000000;    //Write bit=0 DevAddr+W bit[3]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000000;    //Write bit=0 DevAddr+W bit[2]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000000;    //Write bit=0 DevAddr+W bit[1]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000000;    //Write bit=0 DevAddr+W bit[0]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    00000X;    //ACK after DevAddr
                    00001L;    //ACK check (expect LOW)
                    00001L;    //ACK hold
                    00000X;    //SCL↓

                    000000;    //Write bit=0 WordAddr bit[7]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000000;    //Write bit=0 WordAddr bit[6]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000000;    //Write bit=0 WordAddr bit[5]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000001;    //Write bit=1 WordAddr bit[4]
                    000011;    //SCL↑ (data valid)
                    000011;    //SCL high hold
                    000001;    //SCL↓

                    000000;    //Write bit=0 WordAddr bit[3]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000000;    //Write bit=0 WordAddr bit[2]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000000;    //Write bit=0 WordAddr bit[1]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000000;    //Write bit=0 WordAddr bit[0]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    00000X;    //ACK after WordAddr
                    00001L;    //ACK check (expect LOW)
                    00001L;    //ACK hold
                    00000X;    //SCL↓

                    000001;    //Write bit=1 Data bit[7]
                    000011;    //SCL↑ (data valid)
                    000011;    //SCL high hold
                    000001;    //SCL↓

                    000001;    //Write bit=1 Data bit[6]
                    000011;    //SCL↑ (data valid)
                    000011;    //SCL high hold
                    000001;    //SCL↓

                    000000;    //Write bit=0 Data bit[5]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000000;    //Write bit=0 Data bit[4]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000001;    //Write bit=1 Data bit[3]
                    000011;    //SCL↑ (data valid)
                    000011;    //SCL high hold
                    000001;    //SCL↓

                    000000;    //Write bit=0 Data bit[2]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000001;    //Write bit=1 Data bit[1]
                    000011;    //SCL↑ (data valid)
                    000011;    //SCL high hold
                    000001;    //SCL↓

                    000000;    //Write bit=0 Data bit[0]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    00000X;    //ACK after Data
                    00001L;    //ACK check (expect LOW)
                    00001L;    //ACK hold
                    00000X;    //SCL↓

                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000010;    //STOP hold
                    000011;    //STOP Condition (SDA↑)
                    000011;
                    000011;
                    000011;
                    000011;

                    000011;    //=== Byte Write: addr=0x11 data=0xFE ===
                    000011;

                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold

                    000001;    //Write bit=1 DevAddr+W bit[7]
                    000011;    //SCL↑ (data valid)
                    000011;    //SCL high hold
                    000001;    //SCL↓

                    000000;    //Write bit=0 DevAddr+W bit[6]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000001;    //Write bit=1 DevAddr+W bit[5]
                    000011;    //SCL↑ (data valid)
                    000011;    //SCL high hold
                    000001;    //SCL↓

                    000000;    //Write bit=0 DevAddr+W bit[4]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000000;    //Write bit=0 DevAddr+W bit[3]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000000;    //Write bit=0 DevAddr+W bit[2]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000000;    //Write bit=0 DevAddr+W bit[1]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000000;    //Write bit=0 DevAddr+W bit[0]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    00000X;    //ACK after DevAddr
                    00001L;    //ACK check (expect LOW)
                    00001L;    //ACK hold
                    00000X;    //SCL↓

                    000000;    //Write bit=0 WordAddr bit[7]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000000;    //Write bit=0 WordAddr bit[6]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000000;    //Write bit=0 WordAddr bit[5]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000001;    //Write bit=1 WordAddr bit[4]
                    000011;    //SCL↑ (data valid)
                    000011;    //SCL high hold
                    000001;    //SCL↓

                    000000;    //Write bit=0 WordAddr bit[3]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000000;    //Write bit=0 WordAddr bit[2]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000000;    //Write bit=0 WordAddr bit[1]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000001;    //Write bit=1 WordAddr bit[0]
                    000011;    //SCL↑ (data valid)
                    000011;    //SCL high hold
                    000001;    //SCL↓

                    00000X;    //ACK after WordAddr
                    00001L;    //ACK check (expect LOW)
                    00001L;    //ACK hold
                    00000X;    //SCL↓

                    000001;    //Write bit=1 Data bit[7]
                    000011;    //SCL↑ (data valid)
                    000011;    //SCL high hold
                    000001;    //SCL↓

                    000001;    //Write bit=1 Data bit[6]
                    000011;    //SCL↑ (data valid)
                    000011;    //SCL high hold
                    000001;    //SCL↓

                    000001;    //Write bit=1 Data bit[5]
                    000011;    //SCL↑ (data valid)
                    000011;    //SCL high hold
                    000001;    //SCL↓

                    000001;    //Write bit=1 Data bit[4]
                    000011;    //SCL↑ (data valid)
                    000011;    //SCL high hold
                    000001;    //SCL↓

                    000001;    //Write bit=1 Data bit[3]
                    000011;    //SCL↑ (data valid)
                    000011;    //SCL high hold
                    000001;    //SCL↓

                    000001;    //Write bit=1 Data bit[2]
                    000011;    //SCL↑ (data valid)
                    000011;    //SCL high hold
                    000001;    //SCL↓

                    000001;    //Write bit=1 Data bit[1]
                    000011;    //SCL↑ (data valid)
                    000011;    //SCL high hold
                    000001;    //SCL↓

                    000000;    //Write bit=0 Data bit[0]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    00000X;    //ACK after Data
                    00001L;    //ACK check (expect LOW)
                    00001L;    //ACK hold
                    00000X;    //SCL↓

                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000010;    //STOP hold
                    000011;    //STOP Condition (SDA↑)
                    000011;
                    000011;
                    000011;
                    000011;

                    000011;    //=== Random Read: addr=0x10 ===
                    000011;

                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold

                    000001;    //Write bit=1 DevAddr+W bit[7]
                    000011;    //SCL↑ (data valid)
                    000011;    //SCL high hold
                    000001;    //SCL↓

                    000000;    //Write bit=0 DevAddr+W bit[6]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000001;    //Write bit=1 DevAddr+W bit[5]
                    000011;    //SCL↑ (data valid)
                    000011;    //SCL high hold
                    000001;    //SCL↓

                    000000;    //Write bit=0 DevAddr+W bit[4]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000000;    //Write bit=0 DevAddr+W bit[3]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000000;    //Write bit=0 DevAddr+W bit[2]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000000;    //Write bit=0 DevAddr+W bit[1]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000000;    //Write bit=0 DevAddr+W bit[0]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    00000X;    //ACK after DevAddr
                    00001L;    //ACK check (expect LOW)
                    00001L;    //ACK hold
                    00000X;    //SCL↓

                    000000;    //Write bit=0 WordAddr bit[7]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000000;    //Write bit=0 WordAddr bit[6]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000000;    //Write bit=0 WordAddr bit[5]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000001;    //Write bit=1 WordAddr bit[4]
                    000011;    //SCL↑ (data valid)
                    000011;    //SCL high hold
                    000001;    //SCL↓

                    000000;    //Write bit=0 WordAddr bit[3]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000000;    //Write bit=0 WordAddr bit[2]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000000;    //Write bit=0 WordAddr bit[1]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000000;    //Write bit=0 WordAddr bit[0]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    00000X;    //ACK after WordAddr
                    00001L;    //ACK check (expect LOW)
                    00001L;    //ACK hold
                    00000X;    //SCL↓

                    000001;    //RepSTART: SDA↑
                    000011;    //RepSTART: SCL↑
                    000010;    //RepSTART: SDA↓
                    000000;    //RepSTART: SCL↓

                    000001;    //Write bit=1 DevAddr+R bit[7]
                    000011;    //SCL↑ (data valid)
                    000011;    //SCL high hold
                    000001;    //SCL↓

                    000000;    //Write bit=0 DevAddr+R bit[6]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000001;    //Write bit=1 DevAddr+R bit[5]
                    000011;    //SCL↑ (data valid)
                    000011;    //SCL high hold
                    000001;    //SCL↓

                    000000;    //Write bit=0 DevAddr+R bit[4]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000000;    //Write bit=0 DevAddr+R bit[3]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000000;    //Write bit=0 DevAddr+R bit[2]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000000;    //Write bit=0 DevAddr+R bit[1]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000001;    //Write bit=1 DevAddr+R bit[0]
                    000011;    //SCL↑ (data valid)
                    000011;    //SCL high hold
                    000001;    //SCL↓

                    00000X;    //ACK after DevAddr+R
                    00001L;    //ACK check (expect LOW)
                    00001L;    //ACK hold
                    00000X;    //SCL↓

                    00000X;    //Read bit ReadData bit[7]
                    00001H;    //SCL↑ (compare=H)
                    00001H;    //SCL high hold
                    00000X;    //SCL↓

                    00000X;    //Read bit ReadData bit[6]
                    00001H;    //SCL↑ (compare=H)
                    00001H;    //SCL high hold
                    00000X;    //SCL↓

                    00000X;    //Read bit ReadData bit[5]
                    00001L;    //SCL↑ (compare=L)
                    00001L;    //SCL high hold
                    00000X;    //SCL↓

                    00000X;    //Read bit ReadData bit[4]
                    00001L;    //SCL↑ (compare=L)
                    00001L;    //SCL high hold
                    00000X;    //SCL↓

                    00000X;    //Read bit ReadData bit[3]
                    00001H;    //SCL↑ (compare=H)
                    00001H;    //SCL high hold
                    00000X;    //SCL↓

                    00000X;    //Read bit ReadData bit[2]
                    00001L;    //SCL↑ (compare=L)
                    00001L;    //SCL high hold
                    00000X;    //SCL↓

                    00000X;    //Read bit ReadData bit[1]
                    00001H;    //SCL↑ (compare=H)
                    00001H;    //SCL high hold
                    00000X;    //SCL↓

                    00000X;    //Read bit ReadData bit[0]
                    00001L;    //SCL↑ (compare=L)
                    00001L;    //SCL high hold
                    00000X;    //SCL↓

                    000001;    //NACK (end read)
                    000011;    //NACK (SDA=HIGH)
                    000011;    //NACK hold
                    000001;    //SCL↓

                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000010;    //STOP hold
                    000011;    //STOP Condition (SDA↑)

                    000011;    //=== Current Address Read ===
                    000011;

                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold

                    000001;    //Write bit=1 DevAddr+R (Current Addr Read) bit[7]
                    000011;    //SCL↑ (data valid)
                    000011;    //SCL high hold
                    000001;    //SCL↓

                    000000;    //Write bit=0 DevAddr+R (Current Addr Read) bit[6]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000001;    //Write bit=1 DevAddr+R (Current Addr Read) bit[5]
                    000011;    //SCL↑ (data valid)
                    000011;    //SCL high hold
                    000001;    //SCL↓

                    000000;    //Write bit=0 DevAddr+R (Current Addr Read) bit[4]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000000;    //Write bit=0 DevAddr+R (Current Addr Read) bit[3]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000000;    //Write bit=0 DevAddr+R (Current Addr Read) bit[2]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000000;    //Write bit=0 DevAddr+R (Current Addr Read) bit[1]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000001;    //Write bit=1 DevAddr+R (Current Addr Read) bit[0]
                    000011;    //SCL↑ (data valid)
                    000011;    //SCL high hold
                    000001;    //SCL↓

                    00000X;    //ACK after DevAddr+R
                    00001L;    //ACK check (expect LOW)
                    00001L;    //ACK hold
                    00000X;    //SCL↓

                    00000X;    //Read bit CurrentAddrRead data bit[7]
                    00001H;    //SCL↑ (compare=H)
                    00001H;    //SCL high hold
                    00000X;    //SCL↓

                    00000X;    //Read bit CurrentAddrRead data bit[6]
                    00001H;    //SCL↑ (compare=H)
                    00001H;    //SCL high hold
                    00000X;    //SCL↓

                    00000X;    //Read bit CurrentAddrRead data bit[5]
                    00001H;    //SCL↑ (compare=H)
                    00001H;    //SCL high hold
                    00000X;    //SCL↓

                    00000X;    //Read bit CurrentAddrRead data bit[4]
                    00001H;    //SCL↑ (compare=H)
                    00001H;    //SCL high hold
                    00000X;    //SCL↓

                    00000X;    //Read bit CurrentAddrRead data bit[3]
                    00001H;    //SCL↑ (compare=H)
                    00001H;    //SCL high hold
                    00000X;    //SCL↓

                    00000X;    //Read bit CurrentAddrRead data bit[2]
                    00001H;    //SCL↑ (compare=H)
                    00001H;    //SCL high hold
                    00000X;    //SCL↓

                    00000X;    //Read bit CurrentAddrRead data bit[1]
                    00001H;    //SCL↑ (compare=H)
                    00001H;    //SCL high hold
                    00000X;    //SCL↓

                    00000X;    //Read bit CurrentAddrRead data bit[0]
                    00001L;    //SCL↑ (compare=L)
                    00001L;    //SCL high hold
                    00000X;    //SCL↓

                    000001;    //NACK (end current addr read)
                    000011;    //NACK (SDA=HIGH)
                    000011;    //NACK hold
                    000001;    //SCL↓

                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000010;    //STOP hold
                    000011;    //STOP Condition (SDA↑)

                    000011;    //=== Current Address Read Test Complete ===
end:                000011;

@@END_PATTERN_DEFINE
