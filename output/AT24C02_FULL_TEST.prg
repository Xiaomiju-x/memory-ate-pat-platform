//@@历史记录
//   版本号 = v1;
//   日期 = 2026年03月25日;
//   描述
//     设备名称 : AT24C02
//     封装类型 : SOP8
//     协议 : I2C
//     向量总数 : 64182
//     工具 : EEPROM PAT Generator v8.0.0
//   描述结束
//@@历史记录结束

@@SCHEDULE AT24C02_FULL_TEST

    BEFORE_TEST;             // DPS初始化
    OPENSHORT;                // Open/Short Continuity Test
    IIH_IIL;                  // DC Parameter Test
    FUNC_BW;                  // Byte Write + Read
    FUNC_PW;                  // Page Write + Read
    FUNC_BOUND;               // Address Boundary
    FUNC_WP;                  // WP Protect Test
    FUNC_WRAP;                // Page Wrap Test
    FUNC_CAR;                 // Current Address Read
    March_C;                  // March C- Memory Test
    March_B;                  // March B Memory Test
    Addr_Scan;                // Address Space Scan Test
    Data_Retention;           // Data Retention Test
    Error_Test;               // I2C Error/Boundary Test
    Endurance;                // Write Endurance Test

@@END_SCHEDULE

@@EOT

         DIGI_SET_DRV_LEVEL (ALL_PINS, 0V, 0V, 0V);
         WAIT(3MS);
         DIGI_SET_DRIVE_MODE(ALL_PINS, OFF);
         WAIT(3MS);
         DIGI_DPS_SENSE_MODE(INTERNAL_SENSE);

         DIGI_PPMU_FV(ALL_PINS,0V,I4,CONNECT);
         WAIT(3MS);
         DIGI_DPS_FV(VCC, 0V, 250mA, I4,CONNECT);
         WAIT(3MS);
         DIGI_DPS_FV(VCC, 0V, 250mA, I4,DISCONNECT);
         WAIT(3MS);
         DIGI_PPMU_FV(ALL_PINS,0V,I4,DISCONNECT);
         WAIT(3MS);

@@END_EOT


@@PLAN    BEFORE_TEST
  SITE_SEQUENCE      = OFF;
  DISABLE_BY_MARK_NO = NULL;
  GO_THROUGH         = ON;
  REMARK             = BEFORE_TEST;


   DIGI_DPS_SENSE_MODE(EXTERNAL_SENSE);


CONDITION
   IF_FAIL
        REJECT_BIN=1;
 @@END_PLAN


//***************** Open/Short Continuity Test ******************//
@@PLAN    OPENSHORT
  SITE_SEQUENCE      = OFF;
  DISABLE_BY_MARK_NO = NULL;
  GO_THROUGH         = ON;
  REMARK             = OPENSHORT;

   DIGI_SET_DRIVE_MODE(ALLPINS, OFF); 

   DIGI_DPS_FV(VCC, 0.0V, 5mA, I3, CONNECT);
   WAIT(3MS); 

   DIGI_PPMU_WALKING_FI_MV(ALL_PINS,-100uA,I4,UP_LIMIT=-0.2V,DOWN_LIMIT=-1.5V,LOG_ALIAS=OS_GND);  
   C_COMPARE(  A0,  UP_LIMIT=-0.2V,  DOWN_LIMIT=-1.5V,  LOG_ALIAS= OS_GND_A0,   LOG_UNIT=V);
   C_COMPARE(  A1,  UP_LIMIT=-0.2V,  DOWN_LIMIT=-1.5V,  LOG_ALIAS= OS_GND_A1,   LOG_UNIT=V);
   C_COMPARE(  A2,  UP_LIMIT=-0.2V,  DOWN_LIMIT=-1.5V,  LOG_ALIAS= OS_GND_A2,   LOG_UNIT=V);
   C_COMPARE(  SDA, UP_LIMIT=-0.2V,  DOWN_LIMIT=-1.5V,  LOG_ALIAS= OS_GND_SDA,   LOG_UNIT=V);
   C_COMPARE(  SCL, UP_LIMIT=-0.2V,  DOWN_LIMIT=-1.5V,  LOG_ALIAS= OS_GND_SCL,   LOG_UNIT=V);
   C_COMPARE(  WP,  UP_LIMIT=-0.2V,  DOWN_LIMIT=-1.5V,  LOG_ALIAS= OS_GND_WP,   LOG_UNIT=V);

   DIGI_SET_DRIVE_MODE(ALL_PINS,OFF);   
   DIGI_LEVEL_SET(PWR_OFF);

CONDITION
    IF_FAIL
        REJECT_BIN=2;
@@END_PLAN


//***************** DC Parameter Test ******************//
@@PLAN    IIH_IIL
  SITE_SEQUENCE      = OFF;
  DISABLE_BY_MARK_NO = NULL;
  GO_THROUGH         = ON;
  REMARK             = IIH_IIL;

   DIGI_SET_DRIVE_MODE(ALLPINS, OFF); 

   DIGI_LEVEL_SET(DC_0V_PWR);
   WAIT(5NS);
   DIGI_LEVEL_SET(DC_IIH_IIL_LVL);

    //IIH 
   DIGI_PPMU_FV(ALL_PINS,1.8V,I2,CONNECT_NO_CHANGE);     
   WAIT(30mS);
   DIGI_PPMU_MI (ALL_PINS, UP_LIMIT=6.0UA, DOWN_LIMIT=-3.0UA,LOG_ALIAS= IIH,LOG_UNIT=uA);        
   C_COMPARE(  A0,  UP_LIMIT=6.0uA,  DOWN_LIMIT=-3.0uA,  LOG_ALIAS= IIH_A0,   LOG_UNIT=V);
   C_COMPARE(  A1,  UP_LIMIT=6.0uA,  DOWN_LIMIT=-3.0uA,  LOG_ALIAS= IIH_A1,   LOG_UNIT=V);
   C_COMPARE(  A2,  UP_LIMIT=6.0uA,  DOWN_LIMIT=-3.0uA,  LOG_ALIAS= IIH_A2,   LOG_UNIT=V);
   C_COMPARE(  SDA, UP_LIMIT=6.0uA,  DOWN_LIMIT=-3.0uA,  LOG_ALIAS= IIH_SDA,   LOG_UNIT=V);
   C_COMPARE(  SCL, UP_LIMIT=6.0uA,  DOWN_LIMIT=-3.0uA,  LOG_ALIAS= IIH_SCL,   LOG_UNIT=V);
   C_COMPARE(  WP,  UP_LIMIT=6.0uA,  DOWN_LIMIT=-3.0uA,  LOG_ALIAS= IIH_WP,   LOG_UNIT=V);

    //IIL 
   DIGI_PPMU_FV(ALL_PINS,0.0V,I2,CONNECT_NO_CHANGE);     
   WAIT(3mS);
   DIGI_PPMU_MI (ALL_PINS, UP_LIMIT=6.0UA, DOWN_LIMIT=-3.0UA,LOG_ALIAS= IIL,LOG_UNIT=uA);      
   C_COMPARE(  A0,  UP_LIMIT=6.0uA,  DOWN_LIMIT=-3.0uA,  LOG_ALIAS= IIL_A0,   LOG_UNIT=V);
   C_COMPARE(  A1,  UP_LIMIT=6.0uA,  DOWN_LIMIT=-3.0uA,  LOG_ALIAS= IIL_A1,   LOG_UNIT=V);
   C_COMPARE(  A2,  UP_LIMIT=6.0uA,  DOWN_LIMIT=-3.0uA,  LOG_ALIAS= IIL_A2,   LOG_UNIT=V);
   C_COMPARE(  SDA, UP_LIMIT=6.0uA,  DOWN_LIMIT=-3.0uA,  LOG_ALIAS= IIL_SDA,   LOG_UNIT=V);
   C_COMPARE(  SCL, UP_LIMIT=6.0uA,  DOWN_LIMIT=-3.0uA,  LOG_ALIAS= IIL_SCL,   LOG_UNIT=V);
   C_COMPARE(  WP,  UP_LIMIT=6.0uA,  DOWN_LIMIT=-3.0uA,  LOG_ALIAS= IIL_WP,   LOG_UNIT=V);

   DIGI_SET_DRIVE_MODE(ALL_PINS,OFF);   
   DIGI_LEVEL_SET(PWR_OFF);

CONDITION
    IF_FAIL
        REJECT_BIN=3;
@@END_PLAN


//***************** Byte Write + Read ******************//
@@PLAN    FUNC_BW
  SITE_SEQUENCE      = OFF;
  DISABLE_BY_MARK_NO = NULL;
  GO_THROUGH         = ON;
  REMARK             = FUNC_BW;

   DIGI_SET_DRIVE_MODE(ALLPINS, OFF); 

   DIGI_LEVEL_SET(DC_0V_PWR);
   WAIT(5NS);
   DIGI_LEVEL_SET(DC_5_0V_LVL);
   DIGI_SET_DRIVE_MODE(SDA, ACTIVE_LOAD);
   DIGI_SET_ACTIVE_LOAD_CURRENT (SDA, 11MA, 11MA);

   WAIT(3MS);
   RUN_PATTERN(AT24C02_FULL_TEST_FUNC_BW:start,AT24C02_FULL_TEST_FUNC_BW:end,1,LOG_ALIAS=FTR_FUNC_BW);
   WAIT(3MS);

   DIGI_SET_DRIVE_MODE(ALL_PINS,OFF);   
   DIGI_LEVEL_SET(PWR_OFF);

CONDITION
    IF_FAIL
        REJECT_BIN=2;
@@END_PLAN


//***************** Page Write + Read ******************//
@@PLAN    FUNC_PW
  SITE_SEQUENCE      = OFF;
  DISABLE_BY_MARK_NO = NULL;
  GO_THROUGH         = ON;
  REMARK             = FUNC_PW;

   DIGI_SET_DRIVE_MODE(ALLPINS, OFF); 

   DIGI_LEVEL_SET(DC_0V_PWR);
   WAIT(5NS);
   DIGI_LEVEL_SET(DC_5_0V_LVL);
   DIGI_SET_DRIVE_MODE(SDA, ACTIVE_LOAD);
   DIGI_SET_ACTIVE_LOAD_CURRENT (SDA, 11MA, 11MA);

   WAIT(3MS);
   RUN_PATTERN(AT24C02_FULL_TEST_FUNC_PW:start,AT24C02_FULL_TEST_FUNC_PW:end,1,LOG_ALIAS=FTR_FUNC_PW);
   WAIT(3MS);

   DIGI_SET_DRIVE_MODE(ALL_PINS,OFF);   
   DIGI_LEVEL_SET(PWR_OFF);

CONDITION
    IF_FAIL
        REJECT_BIN=2;
@@END_PLAN


//***************** Address Boundary ******************//
@@PLAN    FUNC_BOUND
  SITE_SEQUENCE      = OFF;
  DISABLE_BY_MARK_NO = NULL;
  GO_THROUGH         = ON;
  REMARK             = FUNC_BOUND;

   DIGI_SET_DRIVE_MODE(ALLPINS, OFF); 

   DIGI_LEVEL_SET(DC_0V_PWR);
   WAIT(5NS);
   DIGI_LEVEL_SET(DC_5_0V_LVL);
   DIGI_SET_DRIVE_MODE(SDA, ACTIVE_LOAD);
   DIGI_SET_ACTIVE_LOAD_CURRENT (SDA, 11MA, 11MA);

   WAIT(3MS);
   RUN_PATTERN(AT24C02_FULL_TEST_FUNC_BOUND:start,AT24C02_FULL_TEST_FUNC_BOUND:end,1,LOG_ALIAS=FTR_FUNC_BOUND);
   WAIT(3MS);

   DIGI_SET_DRIVE_MODE(ALL_PINS,OFF);   
   DIGI_LEVEL_SET(PWR_OFF);

CONDITION
    IF_FAIL
        REJECT_BIN=2;
@@END_PLAN


//***************** WP Protect Test ******************//
@@PLAN    FUNC_WP
  SITE_SEQUENCE      = OFF;
  DISABLE_BY_MARK_NO = NULL;
  GO_THROUGH         = ON;
  REMARK             = FUNC_WP;

   DIGI_SET_DRIVE_MODE(ALLPINS, OFF); 

   DIGI_LEVEL_SET(DC_0V_PWR);
   WAIT(5NS);
   DIGI_LEVEL_SET(DC_5_0V_LVL);
   DIGI_SET_DRIVE_MODE(SDA, ACTIVE_LOAD);
   DIGI_SET_ACTIVE_LOAD_CURRENT (SDA, 11MA, 11MA);

   WAIT(3MS);
   RUN_PATTERN(AT24C02_FULL_TEST_FUNC_WP:start,AT24C02_FULL_TEST_FUNC_WP:end,1,LOG_ALIAS=FTR_FUNC_WP);
   WAIT(3MS);

   DIGI_SET_DRIVE_MODE(ALL_PINS,OFF);   
   DIGI_LEVEL_SET(PWR_OFF);

CONDITION
    IF_FAIL
        REJECT_BIN=2;
@@END_PLAN


//***************** Page Wrap Test ******************//
@@PLAN    FUNC_WRAP
  SITE_SEQUENCE      = OFF;
  DISABLE_BY_MARK_NO = NULL;
  GO_THROUGH         = ON;
  REMARK             = FUNC_WRAP;

   DIGI_SET_DRIVE_MODE(ALLPINS, OFF); 

   DIGI_LEVEL_SET(DC_0V_PWR);
   WAIT(5NS);
   DIGI_LEVEL_SET(DC_5_0V_LVL);
   DIGI_SET_DRIVE_MODE(SDA, ACTIVE_LOAD);
   DIGI_SET_ACTIVE_LOAD_CURRENT (SDA, 11MA, 11MA);

   WAIT(3MS);
   RUN_PATTERN(AT24C02_FULL_TEST_FUNC_WRAP:start,AT24C02_FULL_TEST_FUNC_WRAP:end,1,LOG_ALIAS=FTR_FUNC_WRAP);
   WAIT(3MS);

   DIGI_SET_DRIVE_MODE(ALL_PINS,OFF);   
   DIGI_LEVEL_SET(PWR_OFF);

CONDITION
    IF_FAIL
        REJECT_BIN=2;
@@END_PLAN


//***************** Current Address Read ******************//
@@PLAN    FUNC_CAR
  SITE_SEQUENCE      = OFF;
  DISABLE_BY_MARK_NO = NULL;
  GO_THROUGH         = ON;
  REMARK             = FUNC_CAR;

   DIGI_SET_DRIVE_MODE(ALLPINS, OFF); 

   DIGI_LEVEL_SET(DC_0V_PWR);
   WAIT(5NS);
   DIGI_LEVEL_SET(DC_5_0V_LVL);
   DIGI_SET_DRIVE_MODE(SDA, ACTIVE_LOAD);
   DIGI_SET_ACTIVE_LOAD_CURRENT (SDA, 11MA, 11MA);

   WAIT(3MS);
   RUN_PATTERN(AT24C02_FULL_TEST_FUNC_CAR:start,AT24C02_FULL_TEST_FUNC_CAR:end,1,LOG_ALIAS=FTR_FUNC_CAR);
   WAIT(3MS);

   DIGI_SET_DRIVE_MODE(ALL_PINS,OFF);   
   DIGI_LEVEL_SET(PWR_OFF);

CONDITION
    IF_FAIL
        REJECT_BIN=2;
@@END_PLAN


//***************** March C- Memory Test ******************//
@@PLAN    March_C
  SITE_SEQUENCE      = OFF;
  DISABLE_BY_MARK_NO = NULL;
  GO_THROUGH         = ON;
  REMARK             = March_C;

   DIGI_SET_DRIVE_MODE(ALLPINS, OFF); 

   DIGI_LEVEL_SET(DC_0V_PWR);
   WAIT(5NS);
   DIGI_LEVEL_SET(DC_5_0V_LVL);
   DIGI_SET_DRIVE_MODE(SDA, ACTIVE_LOAD);
   DIGI_SET_ACTIVE_LOAD_CURRENT (SDA, 11MA, 11MA);

   WAIT(3MS);
   RUN_PATTERN(AT24C02_FULL_TEST_MARCH:start,AT24C02_FULL_TEST_MARCH:end,1,LOG_ALIAS=FTR_March_C);
   WAIT(3MS);

   DIGI_SET_DRIVE_MODE(ALL_PINS,OFF);   
   DIGI_LEVEL_SET(PWR_OFF);

CONDITION
    IF_FAIL
        REJECT_BIN=5;
@@END_PLAN


//***************** March B Memory Test ******************//
@@PLAN    March_B
  SITE_SEQUENCE      = OFF;
  DISABLE_BY_MARK_NO = NULL;
  GO_THROUGH         = ON;
  REMARK             = March_B;

   DIGI_SET_DRIVE_MODE(ALLPINS, OFF); 

   DIGI_LEVEL_SET(DC_0V_PWR);
   WAIT(5NS);
   DIGI_LEVEL_SET(DC_5_0V_LVL);
   DIGI_SET_DRIVE_MODE(SDA, ACTIVE_LOAD);
   DIGI_SET_ACTIVE_LOAD_CURRENT (SDA, 11MA, 11MA);

   WAIT(3MS);
   RUN_PATTERN(AT24C02_FULL_TEST_MARCHB:start,AT24C02_FULL_TEST_MARCHB:end,1,LOG_ALIAS=FTR_March_B);
   WAIT(3MS);

   DIGI_SET_DRIVE_MODE(ALL_PINS,OFF);   
   DIGI_LEVEL_SET(PWR_OFF);

CONDITION
    IF_FAIL
        REJECT_BIN=6;
@@END_PLAN


//***************** Address Space Scan Test ******************//
@@PLAN    Addr_Scan
  SITE_SEQUENCE      = OFF;
  DISABLE_BY_MARK_NO = NULL;
  GO_THROUGH         = ON;
  REMARK             = Addr_Scan;

   DIGI_SET_DRIVE_MODE(ALLPINS, OFF); 

   DIGI_LEVEL_SET(DC_0V_PWR);
   WAIT(5NS);
   DIGI_LEVEL_SET(DC_5_0V_LVL);
   DIGI_SET_DRIVE_MODE(SDA, ACTIVE_LOAD);
   DIGI_SET_ACTIVE_LOAD_CURRENT (SDA, 11MA, 11MA);

   WAIT(3MS);
   RUN_PATTERN(AT24C02_FULL_TEST_SCAN:start,AT24C02_FULL_TEST_SCAN:end,1,LOG_ALIAS=FTR_Addr_Scan);
   WAIT(3MS);

   DIGI_SET_DRIVE_MODE(ALL_PINS,OFF);   
   DIGI_LEVEL_SET(PWR_OFF);

CONDITION
    IF_FAIL
        REJECT_BIN=7;
@@END_PLAN


//***************** Data Retention Test ******************//
@@PLAN    Data_Retention
  SITE_SEQUENCE      = OFF;
  DISABLE_BY_MARK_NO = NULL;
  GO_THROUGH         = ON;
  REMARK             = Data_Retention;

   DIGI_SET_DRIVE_MODE(ALLPINS, OFF); 

   DIGI_LEVEL_SET(DC_0V_PWR);
   WAIT(5NS);
   DIGI_LEVEL_SET(DC_5_0V_LVL);
   DIGI_SET_DRIVE_MODE(SDA, ACTIVE_LOAD);
   DIGI_SET_ACTIVE_LOAD_CURRENT (SDA, 11MA, 11MA);

   WAIT(3MS);
   RUN_PATTERN(AT24C02_FULL_TEST_RET:start,AT24C02_FULL_TEST_RET:end,1,LOG_ALIAS=FTR_Data_Retention);
   WAIT(3MS);

   DIGI_SET_DRIVE_MODE(ALL_PINS,OFF);   
   DIGI_LEVEL_SET(PWR_OFF);

CONDITION
    IF_FAIL
        REJECT_BIN=8;
@@END_PLAN


//***************** I2C Error/Boundary Test ******************//
@@PLAN    Error_Test
  SITE_SEQUENCE      = OFF;
  DISABLE_BY_MARK_NO = NULL;
  GO_THROUGH         = ON;
  REMARK             = Error_Test;

   DIGI_SET_DRIVE_MODE(ALLPINS, OFF); 

   DIGI_LEVEL_SET(DC_0V_PWR);
   WAIT(5NS);
   DIGI_LEVEL_SET(DC_5_0V_LVL);
   DIGI_SET_DRIVE_MODE(SDA, ACTIVE_LOAD);
   DIGI_SET_ACTIVE_LOAD_CURRENT (SDA, 11MA, 11MA);

   WAIT(3MS);
   RUN_PATTERN(AT24C02_FULL_TEST_ERR:start,AT24C02_FULL_TEST_ERR:end,1,LOG_ALIAS=FTR_Error_Test);
   WAIT(3MS);

   DIGI_SET_DRIVE_MODE(ALL_PINS,OFF);   
   DIGI_LEVEL_SET(PWR_OFF);

CONDITION
    IF_FAIL
        REJECT_BIN=9;
@@END_PLAN


//***************** Write Endurance Test ******************//
@@PLAN    Endurance
  SITE_SEQUENCE      = OFF;
  DISABLE_BY_MARK_NO = NULL;
  GO_THROUGH         = ON;
  REMARK             = Endurance;

   DIGI_SET_DRIVE_MODE(ALLPINS, OFF); 

   DIGI_LEVEL_SET(DC_0V_PWR);
   WAIT(5NS);
   DIGI_LEVEL_SET(DC_5_0V_LVL);
   DIGI_SET_DRIVE_MODE(SDA, ACTIVE_LOAD);
   DIGI_SET_ACTIVE_LOAD_CURRENT (SDA, 11MA, 11MA);

   WAIT(3MS);
   RUN_PATTERN(AT24C02_FULL_TEST_ENDUR:start,AT24C02_FULL_TEST_ENDUR:end,1,LOG_ALIAS=FTR_Endurance);
   WAIT(3MS);

   DIGI_SET_DRIVE_MODE(ALL_PINS,OFF);   
   DIGI_LEVEL_SET(PWR_OFF);

CONDITION
    IF_FAIL
        REJECT_BIN=10;
@@END_PLAN


// ============================================================
// BIN Summary Table
// ============================================================
// BIN  | Name            | Description
// -----|-----------------|----------------------------
//   1  | BEFORE_TEST     | DPS initialization
//   2  | OPENSHORT       | Open/Short Continuity Test
//   3  | IIH_IIL         | DC Parameter Test
//   2  | FUNC_BW         | Byte Write + Read
//   2  | FUNC_PW         | Page Write + Read
//   2  | FUNC_BOUND      | Address Boundary
//   2  | FUNC_WP         | WP Protect Test
//   2  | FUNC_WRAP       | Page Wrap Test
//   2  | FUNC_CAR        | Current Address Read
//   5  | March_C         | March C- Memory Test
//   6  | March_B         | March B Memory Test
//   7  | Addr_Scan       | Address Space Scan Test
//   8  | Data_Retention  | Data Retention Test
//   9  | Error_Test      | I2C Error/Boundary Test
//  10  | Endurance       | Write Endurance Test
// ============================================================
