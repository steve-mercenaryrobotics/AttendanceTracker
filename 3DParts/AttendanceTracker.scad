$fn = 20;
$TotalWidth = 230;
$TotalHeight = 135;
$TotalThickness = 25;

//LCD parameters
$ActiveWidth = 155;
$ActiveHeight = 87;

$PanelWidth = 164.9;
$PanelHeight = 100;
$PanelThicknes = 7.5;

$ModuleWidth = 174.9;
$ModuleHeight = 124.3;
$ModuleClearance = 1;

$PCBThickness = 2;

$TopBorder = 4;
$BottomBorder = $PanelHeight - $ActiveHeight - $TopBorder;
$LeftBorder = 3.2;
$RightBorder = $PanelWidth - $ActiveWidth - $LeftBorder;

$MountHSpacing = 156.9;
$MountVSpacing = 114.96;

$PanelModuleTopOffset = 11;

$LCDMountHoleD = 3;
$PiMountHoleD = 2.5;

//Where to position LCD in shell
$ModuleLeftOffset = 3;
$ModleTopOffset = 5;


$WidthV2 = 247;
$HeightV2 = 129;
$ThicknessV2 = 23.5;
$WallV2 = 4;
$TotalWidthV2 = $WidthV2 + $WallV2 + $WallV2;
$TotalHeightV2 = $HeightV2 + $WallV2 + $WallV2;
$TotalThicknessV2 = $ThicknessV2 + $WallV2 + $WallV2;
$ShellVOffset = -1;


module RoundedBlock($XDim = 10, $YDim = 10, $ZDim = 10, $D1 = 0, $D2 = 0, $D3 = 0, $D4 = 0, $D5 = 0, $D6 = 0, $D7 = 0, $D8 = 0)
{
  $fn = 30;
  hull()
  {
    translate([($XDim - $D1) / 2, ($YDim - $D1) / 2, ($ZDim - $D1)/ 2])
      sphere(d = $D1);
    translate([-($XDim - $D2) / 2, ($YDim - $D2) / 2, ($ZDim - $D2)/ 2])
      sphere(d = $D2);
    translate([-($XDim - $D3) / 2, -($YDim - $D3) / 2, ($ZDim - $D3)/ 2])
      sphere(d = $D3);
    translate([($XDim - $D4) / 2, -($YDim - $D4) / 2, ($ZDim - $D4)/ 2])
      sphere(d = $D4);
    
    translate([($XDim - $D5) / 2, ($YDim - $D5) / 2, -($ZDim - $D5)/ 2])
      sphere(d = $D5);
    translate([-($XDim - $D6) / 2, ($YDim - $D6) / 2, -($ZDim - $D6)/ 2])
      sphere(d = $D6);
    translate([-($XDim - $D7) / 2, -($YDim - $D7) / 2, -($ZDim - $D7)/ 2])
      sphere(d = $D7);
    translate([($XDim - $D8) / 2, -($YDim - $D8) / 2, -($ZDim - $D8)/ 2])
      sphere(d = $D8);
    
  }
}


module PanelTemplate()
{
  //PCB template
  translate([0, 0, $PCBThickness / 2])
    cube([$ModuleWidth + $ModuleClearance, $ModuleHeight + $ModuleClearance, $PCBThickness], center = true);
  //Mount holes
  translate([$MountHSpacing / 2, $MountVSpacing / 2, 0])
    cylinder(d = $LCDMountHoleD, h = 10, center = true);
  translate([-$MountHSpacing / 2, $MountVSpacing / 2, 0])
    cylinder(d = $LCDMountHoleD, h = 10, center = true);
  translate([$MountHSpacing / 2, -$MountVSpacing / 2, 0])
    cylinder(d = $LCDMountHoleD, h = 10, center = true);
  translate([-$MountHSpacing / 2, -$MountVSpacing / 2, 0])
    cylinder(d = $LCDMountHoleD, h = 10, center = true);
  //Panel
  translate([0, (($ModuleHeight - $PanelHeight) / 2) - $PanelModuleTopOffset, ($PCBThickness + $PanelThicknes) / 2])
  {
    cube([$PanelWidth, $PanelHeight, $PanelThicknes], center = true);
    translate([0, 0, 0])
    //Active window
    translate([-(($PanelWidth - $ActiveWidth) / 2) + $LeftBorder, (($PanelHeight - $ActiveHeight) / 2) - $TopBorder, ($PanelThicknes + 3) / 2])
      cube([$ActiveWidth, $ActiveHeight, 3], center = true);
  }
  //Components
  translate([5, 0, -8 / 2])
    cube([160, 98, 8], center = true);
  //LCD connectors
  translate([($ModuleWidth - 15) / 2, (($ModuleHeight - 60) / 2) - 10, -9 / 2])
    cube([15, 60, 10], center = true);
}

module RaspberryPiTemplateZero()
{
  $MountHSpacing = 22.9;
  $MountVSpacing = 57.9;
  //Main body
  translate([0, 0, 2])
    cube([37, 71, 15], center = true);
  //Mount holes
  translate([$MountHSpacing / 2, $MountVSpacing / 2, -5])
    cylinder(d = $PiMountHoleD, h = 10, center = true);
  translate([-$MountHSpacing / 2, $MountVSpacing / 2, -5])
    cylinder(d = $PiMountHoleD, h = 10, center = true);
  translate([$MountHSpacing / 2, -$MountVSpacing / 2, -5])
    cylinder(d = $PiMountHoleD, h = 10, center = true);
  translate([-$MountHSpacing / 2, -$MountVSpacing / 2, -5])
    cylinder(d = $PiMountHoleD, h = 10, center = true);
  
}

module AttendanceTrackerShell()
{
  difference()
  {
    //Main shell
    difference()
    {
      RoundedBlock($XDim = $TotalWidth, $YDim = $TotalHeight, $ZDim = $TotalThickness, $D1 = 5, $D2 = 5, $D3 = 5, $D4 = 5, $D5 = 5, $D6 = 5, $D7 = 5, $D8 = 5);
      translate([-(($TotalWidth - $ModuleWidth) / 2) + $ModuleLeftOffset, (($TotalHeight - $ModuleHeight) / 2) - $ModleTopOffset, 4 - 2])
      {
        //Panel
        PanelTemplate();
        //PI
        translate([(($PanelWidth + 33) / 2) + 23, -($ModuleHeight - 71) / 2, 0])
          RaspberryPiTemplateZero();
        //Connectors
        translate([($ModuleWidth + 58) / 2, 35, 0])
          cube([58, 55, $TotalThickness - 6], center = true);
        //Misc
        translate([($ModuleWidth + 24) / 2, -26.66, 0])
          cube([24, 71, $TotalThickness - 6], center = true);
        //Top clip openings
        translate([0, (($TotalHeight - 5) / 2) - .3635 - 4.5, -3])
          difference()
          {
            cube([140, 5, 10], center = true);
            translate([0, 2.5, 0])
              rotate(90, [0, 1, 0])
                cylinder(d = 1, h = 140, center = true, $fn = 40);
          }
        translate([0, -(($TotalHeight - 5) / 2) + .3635 + 4.5, -3])
          difference()
          {
            cube([140, 5, 10], center = true);
            translate([0, -2.5, 0])
              rotate(90, [0, 1, 0])
                cylinder(d = 1, h = 140, center = true, $fn = 40);
          }
        //Power inlet
        translate([90, -($TotalHeight / 2), 0])
          rotate(90, [1, 0, 0])
            hull()
            {
              cylinder(d = 4.1, h = 20, center = true);
              translate([0, 2, 0])
                cylinder(d = 4.1, h = 20, center = true);
            }
      }
    }
  }
}

module AttendanceTrackerShellBottom()
{
  difference()
  {
    AttendanceTrackerShell();
    translate([0, 0, 24])
      cube([300, 200, 40], center = true);
  }
}

module AttendanceTrackerShellTop()
{
  difference()
  {
    AttendanceTrackerShell();
    translate([0, 0, 24 - 40])
      cube([300, 200, 40], center = true);
  $fn = 40;
  translate([-(($TotalWidth - $ModuleWidth) / 2) + $ModuleLeftOffset, (($TotalHeight - $ModuleHeight) / 2) - $ModleTopOffset, 6.5])
  {
    //Mount holes
    translate([$MountHSpacing / 2, $MountVSpacing / 2, 0])
      cylinder(d = 10, h = 10, center = true);
    translate([-$MountHSpacing / 2, $MountVSpacing / 2, 0])
      cylinder(d = 10, h = 10, center = true);
    translate([$MountHSpacing / 2, -$MountVSpacing / 2, 0])
      cylinder(d = 10, h = 10, center = true);
    translate([-$MountHSpacing / 2, -$MountVSpacing / 2, 0])
      cylinder(d = 10, h = 10, center = true);
  }
  }
  //Top clip tabs
  translate([-(($TotalWidth - $ModuleWidth) / 2) + $ModuleLeftOffset, (($TotalHeight - $ModuleHeight) / 2) - $ModleTopOffset, 4 - 2])
  {
    translate([0, (($TotalHeight - 5) / 2) - .3635 - 4.5, -3])
      difference()
      {
        translate([0, 0.9, 1])
          cube([130, 3, 8], center = true);
        translate([0, 2.5, 0])
          rotate(90, [0, 1, 0])
            cylinder(d = 1.3, h = 140, center = true, $fn = 40);
      }
    translate([0, -(($TotalHeight - 5) / 2) + .3635 + 4.5, -3])
      difference()
      {
        translate([0, -0.9, 1])
          cube([130, 3, 8], center = true);
        translate([0, -2.5, 0])
          rotate(90, [0, 1, 0])
            cylinder(d = 1.3, h = 140, center = true, $fn = 40);
      }
  }
}


module RaspberryPi5()
{
  rotate(-90, [0, 0, 1])
    rotate(90, [1, 0, 0])
//      import("RASPBERRY_PI_5_.stl");
      import("RASPBERRY_PI_5_WITH_ACTIVE_COOLER.stl");
  //Type-C
  translate([-48, 31.3, 3.18])
    cube([40, 14, 9], center = true);
  //HDMI2
  translate([-48, 3.3, 3.05])
    cube([40, 14, 9], center = true);
}

module PanelMountHoles()
{
  translate([$MountHSpacing / 2, $MountVSpacing / 2, 0])
    cylinder(d = $HoleD, h = $Height, center = $center);
  translate([-$MountHSpacing / 2, $MountVSpacing / 2, 0])
    cylinder(d = $HoleD, h = $Height, center = $center);
  translate([$MountHSpacing / 2, -$MountVSpacing / 2, 0])
    cylinder(d = $HoleD, h = $Height, center = $center);
  translate([-$MountHSpacing / 2, -$MountVSpacing / 2, 0])
    cylinder(d = $HoleD, h = $Height, center = $center);
}

module Rp5MountHoles()
{
  $HSpacing = 49;
  $VSpacing = 58;
  
  translate([$HSpacing / 2, $VSpacing / 2, 0])
    cylinder(d = $HoleD, h = $Height, center = $center);
  translate([-$HSpacing / 2, $VSpacing / 2, 0])
    cylinder(d = $HoleD, h = $Height, center = $center);
  translate([$HSpacing / 2, -$VSpacing / 2, 0])
    cylinder(d = $HoleD, h = $Height, center = $center);
  translate([-$HSpacing / 2, -$VSpacing / 2, 0])
    cylinder(d = $HoleD, h = $Height, center = $center);
}

module LCD()
{
  
  //PCB 
  difference()
  {
    translate([0, 0, $PCBThickness / 2])
      cube([$PanelWidth, $ModuleHeight, $PCBThickness], center = true);
    //Mount holes
    PanelMountHoles($HoleD = $LCDMountHoleD, $Height = 10, $center = true);
  }
  //Panel
  translate([0, (($ModuleHeight - $PanelHeight) / 2) - $PanelModuleTopOffset, ($PCBThickness + $PanelThicknes) / 2])
  {
    cube([$PanelWidth, $PanelHeight, $PanelThicknes], center = true);
    translate([0, 0, 0])
    //Active window
    color("Silver")
    translate([-(($PanelWidth - $ActiveWidth) / 2) + $LeftBorder, (($PanelHeight - $ActiveHeight) / 2) - $TopBorder, ($PanelThicknes + .3) / 2])
      cube([$ActiveWidth, $ActiveHeight, .3], center = true);
  }
  //Components
  translate([10 / 2, 0, -8 / 2])
    cube([$PanelWidth - 10, 98, 8], center = true);
  //HDMI
  translate([($PanelWidth + 40) / 2, ($ModuleHeight / 2) - 20, -9 / 2])
    cube([40, 19, 10], center = true);
  //USB
  translate([($PanelWidth + 30) / 2, ($ModuleHeight / 2) - 20 - 18.5, -9 / 2])
    cube([30, 12, 9], center = true);
}

module TypeCCable()
{
  $Spacing = 12.3 - 8.2;
  
  rotate(90, [1, 0, 0])
    hull()
    {
      translate([-$Spacing / 2, 0, 0])
        cylinder(d = $D, h = $H, center = true);
      translate([$Spacing / 2, 0, 0])
        cylinder(d = $D, h = $H, center = true);
    }
}

module TypeCBlock()
{
  $fn = 50;
  difference()
  {
    translate([0, -16, 1])
      cube([22, 58, 13], center = true);
    translate([0, 10, 0])
      TypeCCable($D = 8.2, $H = 25);
    translate([0, -20, 0])
      hull()
      {
        TypeCCable($D = 10, $H = 45);
        translate([0, 0, -10])
          cube([15.2, 45, 1], center = true);
      }
  }
}

module AttendanceTrackerShellV2()
{  
  $LCDSlopeT = $WallV2 * 2;//Should give 45 degrees
  
  translate([38, $ShellVOffset, -3.2])
  {
    //Main shell
    difference()
    {
      //Main body
      color("lightblue", .4)
      RoundedBlock($XDim = $TotalWidthV2, $YDim = $TotalHeightV2, $ZDim = $TotalThicknessV2, $D1 = 5, $D2 = 5, $D3 = 5, $D4 = 5, $D5 = 5, $D6 = 5, $D7 = 5, $D8 = 5);
      //Inside clearance
      cube([$WidthV2, $HeightV2, $ThicknessV2], center = true);
      //Panel opening
      translate([-39.6, 4.9, $ThicknessV2 / 2])
        hull()
        {
          cube([$ActiveWidth, $ActiveHeight, .01], center = true);
          translate([0, 0, $WallV2])
            cube([$ActiveWidth + $LCDSlopeT, $ActiveHeight + $LCDSlopeT, .01], center = true);
        }
      //Ethernet opening
      translate([74.2, -60, -1.5])
        cube([16.5, 20, 14], center = true);
      //USB stack 1 opening
      translate([74.2 - 10.2 + 29.1, -60, .5])
        cube([15, 20, 17.6], center = true);
      //USB stack 2 opening
      translate([74.2 - 10.2 + 47, -60, .5])
        cube([15, 20, 17.6], center = true);
      //Type C socket
//      translate([-80, -$HeightV2 / 2, -6])
//        TypeCCable($D = 10, $H = 25, $fn = 50);
        translate([-6, -24.5, -15])
          cube([37, 14.7, 10], center = true);
        translate([10, -50, -15.2])
        rotate(90, [1, 0, 0])
        cylinder(d = 4, h = 50, $fn = 40, center = true);
      //Pi 5 PCB ckearance
      translate([92, -60, -7.5])
      cube([60, 10, 2], center = true);
      //Cooling openings Left
      for (i = [-3:4])
        translate([$TotalWidthV2 / 2, (i * 6) - 2, 3])
          cube([10, 3, 15], center = true);
      //Cooling openings Right
      for (i = [0:3])
        translate([-$TotalWidthV2 / 2, (i * 6) + 30, 3])
          cube([10, 3, 15], center = true);
      for (i = [0:3])
        translate([-$TotalWidthV2 / 2, (i * 6) - 45, 3])
          cube([10, 3, 15], center = true);
      //LCD screw clearance
      translate([-38, -$ShellVOffset, $ThicknessV2 / 2])
        PanelMountHoles($HoleD = 9, $Height = 2.2, $center = false, $fn = 50);
    }

    translate([-30, -($HeightV2 / 2) + 40, -7.5])
      rotate(90, [0, 0, 1])
        TypeCBlock();
  }

  //LCD supports
  translate([0, 0, (-$ThicknessV2 / 2) - 3.2 - $WallV2])
    difference()
    {
      PanelMountHoles($HoleD = 10, $Height = 18.9, $center = false, $fn = 50);
      PanelMountHoles($HoleD = 2.7, $Height = 19, $center = false, $fn = 50);
    }
  //RP5 stuff
  translate([130, -16.7 + 4, (-$ThicknessV2 / 2) - 3.2 - $WallV2])
  {
    //RP5 supports
    difference()
    {
      Rp5MountHoles($HoleD = 8, $Height = 5.9, $center = false, $fn = 50);
      Rp5MountHoles($HoleD = 2.2, $Height = 19, $center = false, $fn = 50);
    }
  }
  //RFID melt pillars
  translate([($WidthV2 / 2) + 38 - (37 / 2) - 18, ($HeightV2 / 2) - (35 / 2) - 5, ($ThicknessV2 / 2) - 3.2 - $WallV2])
    RFIDPillars();
}

module RFIDPillars()
{
  $VSpacing1 = 24.88;
  $VSpacing2 = 34.25;
  $HSpacing  = 37.6;
  
  translate([$HSpacing / 2, $VSpacing2 / 2, 0])
    cylinder(d = 3.1, h = 4);
  translate([$HSpacing / 2, -$VSpacing2 / 2, 0])
    cylinder(d = 3.1, h = 4);
  translate([-$HSpacing / 2, $VSpacing1 / 2, 0])
    cylinder(d = 3.1, h = 4);
  translate([-$HSpacing / 2, -$VSpacing1 / 2, 0])
    cylinder(d = 3.1, h = 4);
}

module LowerClip()
{
  $H = 23;
  $Thickness = 2.5;
  
  translate([0, $Thickness / 2, -($TotalThicknessV2 - $H) / 2])
  {
    cube([$L, $Thickness, $H], center = true);
    translate([0, -.3, ($H / 2) - 1.83])
      rotate(-10, [1, 0, 0])
        cube([$L, $Thickness, 3], center = true);
  }  
}

module ClipSet()
{
  //Front
  translate([20, - ($HeightV2 / 2) + $ShellVOffset, 0])
    LowerClip($L = 90);
  //Back
  mirror([0, 1, 0])
    translate([20, - ($HeightV2 / 2) - $ShellVOffset, 0])
      LowerClip($L = 90);
  //Left
  translate([-($WidthV2 / 2) + 38, 0, 0])
    rotate(-90, [0, 0, 1])
      LowerClip($L = 50);
  //right
  translate([($WidthV2 / 2) + 38, -35, 0])
    rotate(90, [0, 0, 1])
      LowerClip($L = 20 + $Extend);
  translate([($WidthV2 / 2) + 38, 40, 0])
    rotate(90, [0, 0, 1])
      LowerClip($L = 30 + $Extend);
}

module LowerShellSegmentV2()
{
  //Shell core
  difference()
  {
    AttendanceTrackerShellV2();
    translate([40, 0, (50 / 2) + 2])
      cube([300, 200, 50], center = true);
  }
  //Clips
  ClipSet($Extend = 0);
}

module UpperShellSegmentV2()
{
  difference()
  {
    AttendanceTrackerShellV2();
    translate([40, 0, -(50 / 2) + 2])
      cube([300, 200, 50], center = true);

  //Clips
  ClipSet($Extend = 3);
  }
}


//RaspberryPiTemplateZero();
//PanelTemplate();
/*
difference()
{
  union()
  {
    AttendanceTrackerShellBottom();
    AttendanceTrackerShellTop();
  }
  translate([0, -100, -25])
    cube([300, 200, 50]);
}
*/

//AttendanceTrackerShellBottom();
//AttendanceTrackerShellTop();
//PanelTemplate();

//LCD();
//translate([130, -16.7 - 6, -13])
//  RaspberryPi5();

//LowerShellSegmentV2();
UpperShellSegmentV2();
