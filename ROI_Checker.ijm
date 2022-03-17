/*
 *  Automatically segements localization generated data from a results table and image
 *
 *  2022
 *  
 *  Author: Kierran Falloon
 *  University of Strathclyde, Glasgow, Scotland
 *  4th Year Mphys Physics with Advanced Research
 *  
 *  Created with help and guidance from Sebastian van de Linde (s.vandelinde@strath.ac.uk)
 *  To be used in conjunction with associated python scripts to estimate precision
 *  
 */
 
choices = initialdialog();
operation = choices[0];
pixelsize = choices[1];
running =  choices[2];

while(running == true){
	if(isOpen("Results") == false) exit("Please load a localization file");
	if(operation == "Segment"){
		segment();
		
		choices = initialdialog();
		operation = choices[0];
		pixelsize = choices[1];
		running =  choices[2];
	}
	if(operation == "Circularise ROIs"){
		if(isOpen("ROI Manager") == false){
			run("ROI Manager...");
			roiManager("delete");
		}
		circularise_rois();
		
		choices = initialdialog();
		operation = choices[0];
		pixelsize = choices[1];
		running =  choices[2];
	}
	if(operation == "Mean-centre ROIs"){
		if(isOpen("ROI Manager") == false){
			run("ROI Manager...");
			roiManager("delete");
		}
		mean_centre(pixelsize);
		
		choices = initialdialog();
		operation = choices[0];
		pixelsize = choices[1];
		running =  choices[2];
	}
}

if(running == false){
	if(operation == "Segment"){
		if(isOpen("Results") == false) exit("Please load a localization file");
		segment();
	}
	if(operation == "Circularise ROIs"){
		if(isOpen("ROI Manager") == false){
			run("ROI Manager...");
			roiManager("delete");
		}
		circularise_rois();
	}
	if(operation == "Mean-centre ROIs"){
		if(isOpen("Results") == false) exit("Please load a localization file");
		if(isOpen("ROI Manager") == false){
			run("ROI Manager...");
			roiManager("delete");
		}
		mean_centre(pixelsize);
	}
	
	run("Quit");
}

/* Functions */

function initialdialog(){
	 /***** GUI *****/
	version = "1.0";
	filename = File.getName("Filter-segment.ijm");
	items = newArray("Segment", "Circularise ROIs", "Mean-centre ROIs");
	html = html_message();
	Dialog.create("ROI Checker " + version);
	Dialog.setInsets(0,0,0);
	Dialog.addMessage("Choose an operation:");
	
	Dialog.addChoice("Operation", items);
	Dialog.addNumber("Pixel size [nm]", 10);
	Dialog.addCheckbox("Relaunch?", 1);
	Dialog.addHelp(html);
	
	Dialog.show();
	
	operation = Dialog.getChoice();
	pixelsize = Dialog.getNumber();
	running = Dialog.getCheckbox();
	return newArray(operation, pixelsize, running);
}

function segment(){
	Dialog.create("Segment");
	Dialog.addMessage("Define ROI");
	Dialog.addCheckbox("Draw ROI", 1);
	/***
	Dialog.addMessage("If Draw ROI is ticked, ignore following");
	Dialog.addNumber("x [µm]", 0);
	Dialog.addNumber("y [µm]", 0);
	Dialog.addNumber("w [µm]", 0);
	Dialog.addNumber("h [µm]", 0);
	***/
	Dialog.addMessage("Threshold options:");
	Dialog.addCheckbox("Auto Threshold", 1);
	/***
	Dialog.addMessage("If Auto Threshold is ticked, ignore following");
	threshold_options = newArray("Default", "Huang");
	Dialog.addChoice("", threshold_options);
	Dialog.addSlider("Upper threshold", 0, 1000, 1e30);
	Dialog.addSlider("Upper threshold", 0, 0, 0);
	/***/
	Dialog.show();
	
	draw = Dialog.getCheckbox();
	auto = Dialog.getCheckbox();
	if(draw == false){
		if(auto == true){
		Dialog.create("Options")
		Dialog.addMessage("ROI options:");
		Dialog.addNumber("x [µm]", 0);
		Dialog.addNumber("y [µm]", 0);
		Dialog.addNumber("w [µm]", 0);
		Dialog.addNumber("h [µm]", 0);
		Dialog.show();
		roix = Dialog.getNumber()/pixelsize;
		roiy = Dialog.getNumber()/pixelsize;
		roiw = Dialog.getNumber()/pixelsize;
		roih = Dialog.getNumber()/pixelsize;
	}else{
		Dialog.create("Options")
		threshold_options = newArray("Default", "Huang");
		Dialog.addMessage("ROI options:");
		Dialog.addNumber("x [µm]", 0);
		Dialog.addNumber("y [µm]", 0);
		Dialog.addNumber("w [µm]", 0);
		Dialog.addNumber("h [µm]", 0);
		Dialog.addMessage("Threshold options:");
		Dialog.addChoice("", threshold_options);
		Dialog.addSlider("Upper threshold", 0, 1000, 1e30);
		Dialog.addSlider("Upper threshold", 0, 0, 0);
		Dialog.show();
		roix = Dialog.getNumber()/pixelsize;
		roiy = Dialog.getNumber()/pixelsize;
		roiw = Dialog.getNumber()/pixelsize;
		roih = Dialog.getNumber()/pixelsize;
		threshchoice = Dialog.getChoice();
		uthresh = Dialog.getNumber();
		lthresh = Dialog.getNumber();
		}
	}
	if(draw==true){
		if(auto == true){
			continue;
		}
		else{
			
			Dialog.create("Options")
			Dialog.addMessage("Threshold options:");
			threshold_options = newArray("Default", "Huang");
			Dialog.addChoice("", threshold_options);
			Dialog.addSlider("Upper threshold", 0, 1000, 1e30);
			Dialog.addSlider("Upper threshold", 0, 0, 0);
			Dialog.show();
			threshchoice = Dialog.getChoice();
			uthresh = Dialog.getNumber();
			lthresh = Dialog.getNumber();
		}
	}
	
	/***
	if(auto == false){
		threshold_options = newArray("Default", "Huang");
		Dialog.addChoice("", threshold_options);
		Dialog.addSlider("Upper threshold", 0, 1000, 1e30);
		Dialog.addSlider("Upper threshold", 0, 0, 0);
		Dialog.show();
		threshchoice = Dialog.getChoice();
		uthresh = Dialog.getNumber();
		lthresh = Dialog.getNumber();
	}
	***/
	title = getTitle();
	selectWindow(title);
	dupetitle = title+"_dupe";
	run("Duplicate...", dupetitle);
	dupetitle = getTitle();
	
	if(auto == true){
		if(threshchoice == "Default"){
			setAutoThreshold("Default dark no-reset");
		} else 
			setAutoThreshold("Huang dark no-reset");
		} else
			if(threshchoice == "Default"){
				setThreshold(lthresh, uthresh);
		} else
			setThreshold(lthresh, uthresh);
			
	selectWindow(dupetitle);
	run("Create Mask");
	
	if(draw == true){
		waitForUser("Draw ROI");
	} else{
		makeRectangle(roix, roiy, roiw, roih);
	}
	
	selectWindow(dupetitle);
	run("Restore Selection");
	run("Clear Outside");
	run("Create Selection");
	selectWindow("mask");
	close();
	selectWindow(dupetitle);
	
	keepchoice = newArray("Yes", "No");
	Dialog.create("Keep the segment?");
	Dialog.addChoice("", keepchoice);
	Dialog.show();
	keep = Dialog.getChoice();
	
	if(keep == "Yes"){
		selectWindow(title);
		run("Restore Selection");
		run("Clear Outside");
		selectWindow(dupetitle);
		close();
	} else{
		selectWindow(dupetitle);
		close();
		selectWindow(title);
		segment();
	}
}

function circularise_rois(){
	Dialog.create("Circularise ROIs");
	Dialog.addMessage("Circularise ROIs");
	Dialog.addNumber("Define sigma:", 1);
	Dialog.addSlider("Lower circularity threshold", 0.0, 1, 0.9);
	Dialog.show();
	
	sigma = Dialog.getNumber();
	circlow = Dialog.getNumber();
	
	title = getTitle();
	getDimensions(width, height, channels, slices, frames);
	run("Gaussian Blur...", sigma);
	makeRectangle(0, 0, width, height);
	setOption("BlackBackground", false);
	run("Convert to Mask");
	run("Analyze Particles...", "  circularity=circlow 1 show=Overlay exclude include add");
	selectWindow(title);
	run("Restore Selection");
}

function mean_centre(pixelsize){
	numROIs = roiManager("count");
		
	f = File.open("");
	print(f, "\"x [nm]\" "+","+ "\"y [nm]\" ");
	Rows = 0;
	headings = split(Table.headings(), "\t" ); // Get table headings (different for thunderstorm and rapidstorm)
	x = Table.getColumn(headings[2]);
	y = Table.getColumn(headings[3]);
	
	for(i=0; i<numROIs; i++) { // loop through ROIs (analyzed particles)
		showProgress(-i+1/numROIs, numROIs);
		roiManager("Select", i); // Select i-th roi
		Rows = 0;
		
		for (j = 0; j < nResults(); j++) { // Loop through Results table
		    if (Roi.contains(floor(x[j]/pixelsize), floor(y[j]/pixelsize)) == true) { // If coordinate in ROI
		    	Rows += 1;

		    }
		}
		xarray = newArray(Rows); // Creates appropriately sized array for ROi
		yarray = newArray(Rows); // To avoid 0's (if sized generically) impacting mean of array
		
		k=0;
		for (j = 0; j < nResults(); j++) { // Loop through Results table
			if (Rows == NaN)
				break;
		    if (Roi.contains(floor(x[j]/pixelsize), floor(y[j]/pixelsize)) == true) { // If coordinate in ROI
		    	xarray[k] = x[j]/pixelsize;
		    	yarray[k] = y[j]/pixelsize;
		    	k+=1;
		    }
		}
		// Weighing each ROI against the mean
		Array.getStatistics(xarray, min, max, mean, stdDev); 
		for (j = 0; j < xarray.length; j++) {
			if (Rows == NaN)
				break;
			xarray[j] = xarray[j] - mean;
		}
		
		Array.getStatistics(yarray, min, max, mean, stdDev);
		for (j = 0; j < yarray.length; j++) {
			if (Rows == NaN)
				break;
			yarray[j] = yarray[j] - mean;
		}
		
		for (j = 0; j < yarray.length; j++) {
			if (Rows == NaN)
				break;
			print(f, xarray[j]+","+yarray[j]);
		}
	} File.close(f);
} 


function html_message(){
text = "<html>"
	+"<h3>ROI Checker</h3>"
	+"<h4>Operations</h4>"
	+"<b>Operation:</b> select one of the following:<br>"
	+"<b>Segment</b>: Segments data according to process laid out at <A HREF=https://imagej.net/imaging/segmentation> the ImageJ wiki </A>.<br>"
	+"<b>Circularise ROIs</b>: Circularises each cluster of localizations using a gaussian fit with user-specified sigma.<br>"
	+"<b>Mean-centre ROIs</b>: Subtracts the mean of localization positions within each individual ROI from the position of the ROI, <br>"
	+"such that all localizations are centered around (0,0). It is then saved to 'log.txt', in CSV format, for postprocessing.<br>" 
	+"<small> Kierran Falloon, submitted in partial fulfilment for the degree of MPhys Physics with Advanced Research "
	+"</font>";
	return text;