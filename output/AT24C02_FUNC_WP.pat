// PAT File: FUNC_WP
// Description: WP Protect Test
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
// FUNC_WP
// A0,A1,A2,WP,SCL,SDA

start:              000011;AC_SET 1;

                    000011;    //=== Byte Write: addr=0x40 data=0x5A ===
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

                    000001;    //Write bit=1 WordAddr bit[6]
                    000011;    //SCL↑ (data valid)
                    000011;    //SCL high hold
                    000001;    //SCL↓

                    000000;    //Write bit=0 WordAddr bit[5]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000000;    //Write bit=0 WordAddr bit[4]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

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

                    000000;    //Write bit=0 Data bit[7]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000001;    //Write bit=1 Data bit[6]
                    000011;    //SCL↑ (data valid)
                    000011;    //SCL high hold
                    000001;    //SCL↓

                    000000;    //Write bit=0 Data bit[5]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000001;    //Write bit=1 Data bit[4]
                    000011;    //SCL↑ (data valid)
                    000011;    //SCL high hold
                    000001;    //SCL↓

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

                    000111;    //=== Byte Write: addr=0x40 data=0xA5 ===
                    000111;

                    000111;    //START Setup
                    000110;    //START Condition (SDA↓)
                    000100;    //START Hold

                    000101;    //Write bit=1 DevAddr+W bit[7]
                    000111;    //SCL↑ (data valid)
                    000111;    //SCL high hold
                    000101;    //SCL↓

                    000100;    //Write bit=0 DevAddr+W bit[6]
                    000110;    //SCL↑ (data valid)
                    000110;    //SCL high hold
                    000100;    //SCL↓

                    000101;    //Write bit=1 DevAddr+W bit[5]
                    000111;    //SCL↑ (data valid)
                    000111;    //SCL high hold
                    000101;    //SCL↓

                    000100;    //Write bit=0 DevAddr+W bit[4]
                    000110;    //SCL↑ (data valid)
                    000110;    //SCL high hold
                    000100;    //SCL↓

                    000100;    //Write bit=0 DevAddr+W bit[3]
                    000110;    //SCL↑ (data valid)
                    000110;    //SCL high hold
                    000100;    //SCL↓

                    000100;    //Write bit=0 DevAddr+W bit[2]
                    000110;    //SCL↑ (data valid)
                    000110;    //SCL high hold
                    000100;    //SCL↓

                    000100;    //Write bit=0 DevAddr+W bit[1]
                    000110;    //SCL↑ (data valid)
                    000110;    //SCL high hold
                    000100;    //SCL↓

                    000100;    //Write bit=0 DevAddr+W bit[0]
                    000110;    //SCL↑ (data valid)
                    000110;    //SCL high hold
                    000100;    //SCL↓

                    00010X;    //ACK after DevAddr
                    00011L;    //ACK check (expect LOW)
                    00011L;    //ACK hold
                    00010X;    //SCL↓

                    000100;    //Write bit=0 WordAddr bit[7]
                    000110;    //SCL↑ (data valid)
                    000110;    //SCL high hold
                    000100;    //SCL↓

                    000101;    //Write bit=1 WordAddr bit[6]
                    000111;    //SCL↑ (data valid)
                    000111;    //SCL high hold
                    000101;    //SCL↓

                    000100;    //Write bit=0 WordAddr bit[5]
                    000110;    //SCL↑ (data valid)
                    000110;    //SCL high hold
                    000100;    //SCL↓

                    000100;    //Write bit=0 WordAddr bit[4]
                    000110;    //SCL↑ (data valid)
                    000110;    //SCL high hold
                    000100;    //SCL↓

                    000100;    //Write bit=0 WordAddr bit[3]
                    000110;    //SCL↑ (data valid)
                    000110;    //SCL high hold
                    000100;    //SCL↓

                    000100;    //Write bit=0 WordAddr bit[2]
                    000110;    //SCL↑ (data valid)
                    000110;    //SCL high hold
                    000100;    //SCL↓

                    000100;    //Write bit=0 WordAddr bit[1]
                    000110;    //SCL↑ (data valid)
                    000110;    //SCL high hold
                    000100;    //SCL↓

                    000100;    //Write bit=0 WordAddr bit[0]
                    000110;    //SCL↑ (data valid)
                    000110;    //SCL high hold
                    000100;    //SCL↓

                    00010X;    //ACK after WordAddr
                    00011L;    //ACK check (expect LOW)
                    00011L;    //ACK hold
                    00010X;    //SCL↓

                    000101;    //Write bit=1 Data bit[7]
                    000111;    //SCL↑ (data valid)
                    000111;    //SCL high hold
                    000101;    //SCL↓

                    000100;    //Write bit=0 Data bit[6]
                    000110;    //SCL↑ (data valid)
                    000110;    //SCL high hold
                    000100;    //SCL↓

                    000101;    //Write bit=1 Data bit[5]
                    000111;    //SCL↑ (data valid)
                    000111;    //SCL high hold
                    000101;    //SCL↓

                    000100;    //Write bit=0 Data bit[4]
                    000110;    //SCL↑ (data valid)
                    000110;    //SCL high hold
                    000100;    //SCL↓

                    000100;    //Write bit=0 Data bit[3]
                    000110;    //SCL↑ (data valid)
                    000110;    //SCL high hold
                    000100;    //SCL↓

                    000101;    //Write bit=1 Data bit[2]
                    000111;    //SCL↑ (data valid)
                    000111;    //SCL high hold
                    000101;    //SCL↓

                    000100;    //Write bit=0 Data bit[1]
                    000110;    //SCL↑ (data valid)
                    000110;    //SCL high hold
                    000100;    //SCL↓

                    000101;    //Write bit=1 Data bit[0]
                    000111;    //SCL↑ (data valid)
                    000111;    //SCL high hold
                    000101;    //SCL↓

                    00010X;    //ACK after Data
                    00011L;    //ACK check (expect LOW)
                    00011L;    //ACK hold
                    00010X;    //SCL↓

                    000100;    //STOP Setup
                    000110;    //STOP (SCL↑)
                    000110;    //STOP hold
                    000111;    //STOP Condition (SDA↑)
                    000111;
                    000111;
                    000111;
                    000111;

                    000011;    //=== Random Read: addr=0x40 ===
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

                    000001;    //Write bit=1 WordAddr bit[6]
                    000011;    //SCL↑ (data valid)
                    000011;    //SCL high hold
                    000001;    //SCL↓

                    000000;    //Write bit=0 WordAddr bit[5]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000000;    //Write bit=0 WordAddr bit[4]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

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
                    00001L;    //SCL↑ (compare=L)
                    00001L;    //SCL high hold
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
                    00001H;    //SCL↑ (compare=H)
                    00001H;    //SCL high hold
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

                    000011;    //=== WP Test Complete ===
end:                000011;

@@END_PATTERN_DEFINE
