// PAT File: FUNC_WP_ACK_POLL
// Description: WP Protect Test - ACK Polling
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
// FUNC_WP_ACK_POLL
// A0,A1,A2,WP,SCL,SDA

start:              000011;AC_SET 1;
                    000011;

                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold

                    000001;    //Write bit=1 Poll attempt 0 bit[7]
                    000011;    //SCL↑ (data valid)
                    000011;    //SCL high hold
                    000001;    //SCL↓

                    000000;    //Write bit=0 Poll attempt 0 bit[6]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000001;    //Write bit=1 Poll attempt 0 bit[5]
                    000011;    //SCL↑ (data valid)
                    000011;    //SCL high hold
                    000001;    //SCL↓

                    000000;    //Write bit=0 Poll attempt 0 bit[4]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000000;    //Write bit=0 Poll attempt 0 bit[3]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000000;    //Write bit=0 Poll attempt 0 bit[2]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000000;    //Write bit=0 Poll attempt 0 bit[1]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000000;    //Write bit=0 Poll attempt 0 bit[0]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    00000Z;    //Poll NACK (device busy, attempt 0)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓

                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000010;    //STOP hold
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;

                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold

                    000001;    //Write bit=1 Poll attempt 1 bit[7]
                    000011;    //SCL↑ (data valid)
                    000011;    //SCL high hold
                    000001;    //SCL↓

                    000000;    //Write bit=0 Poll attempt 1 bit[6]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000001;    //Write bit=1 Poll attempt 1 bit[5]
                    000011;    //SCL↑ (data valid)
                    000011;    //SCL high hold
                    000001;    //SCL↓

                    000000;    //Write bit=0 Poll attempt 1 bit[4]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000000;    //Write bit=0 Poll attempt 1 bit[3]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000000;    //Write bit=0 Poll attempt 1 bit[2]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000000;    //Write bit=0 Poll attempt 1 bit[1]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    000000;    //Write bit=0 Poll attempt 1 bit[0]
                    000010;    //SCL↑ (data valid)
                    000010;    //SCL high hold
                    000000;    //SCL↓

                    00000X;    //Poll ACK (device ready, attempt 1)
                    00001L;    //ACK check (expect LOW)
                    00001L;    //ACK hold
                    00000X;    //SCL↓

                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000010;    //STOP hold
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
WP_PROTECT:         000111;    //WP=1: write protect enabled, attempt overwrite (data unchanged)

                    000111;    //=== ACK Polling (wait for write cycle) ===
                    000111;

                    000111;    //START Setup
                    000110;    //START Condition (SDA↓)
                    000100;    //START Hold

                    000101;    //Write bit=1 Poll attempt 0 bit[7]
                    000111;    //SCL↑ (data valid)
                    000111;    //SCL high hold
                    000101;    //SCL↓

                    000100;    //Write bit=0 Poll attempt 0 bit[6]
                    000110;    //SCL↑ (data valid)
                    000110;    //SCL high hold
                    000100;    //SCL↓

                    000101;    //Write bit=1 Poll attempt 0 bit[5]
                    000111;    //SCL↑ (data valid)
                    000111;    //SCL high hold
                    000101;    //SCL↓

                    000100;    //Write bit=0 Poll attempt 0 bit[4]
                    000110;    //SCL↑ (data valid)
                    000110;    //SCL high hold
                    000100;    //SCL↓

                    000100;    //Write bit=0 Poll attempt 0 bit[3]
                    000110;    //SCL↑ (data valid)
                    000110;    //SCL high hold
                    000100;    //SCL↓

                    000100;    //Write bit=0 Poll attempt 0 bit[2]
                    000110;    //SCL↑ (data valid)
                    000110;    //SCL high hold
                    000100;    //SCL↓

                    000100;    //Write bit=0 Poll attempt 0 bit[1]
                    000110;    //SCL↑ (data valid)
                    000110;    //SCL high hold
                    000100;    //SCL↓

                    000100;    //Write bit=0 Poll attempt 0 bit[0]
                    000110;    //SCL↑ (data valid)
                    000110;    //SCL high hold
                    000100;    //SCL↓

                    00010Z;    //Poll NACK (device busy, attempt 0)
                    00011H;    //NACK check (expect HIGH)
                    00010X;    //SCL↓

                    000100;    //STOP Setup
                    000110;    //STOP (SCL↑)
                    000110;    //STOP hold
                    000111;    //STOP Condition (SDA↑)
                    000111;    //Poll interval
                    000111;

                    000111;    //START Setup
                    000110;    //START Condition (SDA↓)
                    000100;    //START Hold

                    000101;    //Write bit=1 Poll attempt 1 bit[7]
                    000111;    //SCL↑ (data valid)
                    000111;    //SCL high hold
                    000101;    //SCL↓

                    000100;    //Write bit=0 Poll attempt 1 bit[6]
                    000110;    //SCL↑ (data valid)
                    000110;    //SCL high hold
                    000100;    //SCL↓

                    000101;    //Write bit=1 Poll attempt 1 bit[5]
                    000111;    //SCL↑ (data valid)
                    000111;    //SCL high hold
                    000101;    //SCL↓

                    000100;    //Write bit=0 Poll attempt 1 bit[4]
                    000110;    //SCL↑ (data valid)
                    000110;    //SCL high hold
                    000100;    //SCL↓

                    000100;    //Write bit=0 Poll attempt 1 bit[3]
                    000110;    //SCL↑ (data valid)
                    000110;    //SCL high hold
                    000100;    //SCL↓

                    000100;    //Write bit=0 Poll attempt 1 bit[2]
                    000110;    //SCL↑ (data valid)
                    000110;    //SCL high hold
                    000100;    //SCL↓

                    000100;    //Write bit=0 Poll attempt 1 bit[1]
                    000110;    //SCL↑ (data valid)
                    000110;    //SCL high hold
                    000100;    //SCL↓

                    000100;    //Write bit=0 Poll attempt 1 bit[0]
                    000110;    //SCL↑ (data valid)
                    000110;    //SCL high hold
                    000100;    //SCL↓

                    00010X;    //Poll ACK (device ready, attempt 1)
                    00011L;    //ACK check (expect LOW)
                    00011L;    //ACK hold
                    00010X;    //SCL↓

                    000100;    //STOP Setup
                    000110;    //STOP (SCL↑)
                    000110;    //STOP hold
                    000111;    //STOP Condition (SDA↑)
                    000111;    //Poll interval
                    000111;
end:                000011;    //WP=0: read back to verify data unchanged (expect 0x5A)

@@END_PATTERN_DEFINE
