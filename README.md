![SideFXEDU logo](https://github.com/brunoebe/SideFXEDU/blob/Development/help/images/sidefxedu_full.png)
# SideFX EDU | Education Driven Utilities

SideFX EDU is a completely free, open-source toolset geared towards assisting Houdini Instructors with a variety of tasks commonly used when teaching Houdini. It is an all-inclusive toolset that spans the shelf, digital assets, custom desktops and scripts and more. The toolset is currently maintained by the SideFX Education and Training team. It also receives a lot of contributions from the always active Houdini instructors community. This toolset originated from the SideFX Labs toolset, which inspired us. 

# Requirements

This toolset requires SideFX Labs to be installed. Please visit the [SideFX Labs page](https://www.sidefx.com/docs/houdini/labs/) for further instructions.

# Installation

The following instructions are based on the **Windows OS**. Please adapt them accordingly to your OS.

## Using GitHub

Step 1. Click on the top-right **Code** button on the main page of this repository and select **Download ZIP**. This allows you to get the latest update.

Step 2. If you have downloaded a zipped version of the package in Step 1, unzip it into a custom SideFXEDU directory of your choosing.

Step 3. Go to your custom SideFXEDU directory that now contains the unzipped contents, copy the package definition template file `SideFXEDU.json` to `C:\Users\...\Documents\houdini19.5\packages`. 
Note: the default Houdini installation does not create a 'packages' folder, so you might have to create it if it does not exist. 
Rename the destination copy to `SideFXEDU19.5.json`. Open this file and replace `"$HOUDINI_PACKAGE_PATH/SideFXEDU19.5"` (line 8) with the path to your own SideFXEDU directory. When Houdini launches, it relies on this file to discover the location of your SideFX EDU package.

(Step 3 only needs to be done once for every major Houdini X.Y release. To update SideFX EDU for the same Houdini X.Y version, simply delete the existing contents of your custom SideFXEDU directory and unzip the updated package into that folder.)

For more on how to manage Houdini packages, please visit [here](https://www.sidefx.com/docs/houdini/ref/plugins.html).

## Verification
If SideFX EDU is successfully installed, launch Houdini and you should see a **Education** menu on the top-left menu bar.

# Additional Information

## Expanded HDAs
All of the HDAs are using the expanded format that was introduced in H16. This allows better diffing of the tools so you can see what our changes are doing and choose to integrate them back into your production.

## Example Files
Instead of tying the examples as HDAs, we will be generating separate hip files that show how the tools should work in context. These can be found [here](https://github.com/sideeffects/SideFXEDU/tree/Development/hip).

## Data Analytics
SideFX EDU *optionally* collects data about what tools are used through Google Analytics. We do this in order to focus our resources on the more active tools and therefore be able to help more people. This does *not* track any personal user data such as IP, Name, License use etc. To opt-out of this tracking, you can disable the "Send Anonymous Usage Statistics" toggle under preferences. Additionally, you can bypass this behavior entirely by setting the environment variable "HOUDINI_ANONYMOUS_STATISTICS = 0".

## Contributors
### SideFX Education and Training Team
- Bruno Ébé
- Peter Arcara

### Instructors Community
- Albert Szostkiewicz
