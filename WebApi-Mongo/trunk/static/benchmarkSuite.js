var $ = function(id) {
      return document.getElementById(id);
} 

var startTimes = {};
var results = [];

var getTimeElapsed = function(sDate){
	return (new Date()).getTime() - sDate.getTime();
}

var toggle = function(id){
	var elem = $(id);
	if(elem.style.display == "block"){
		$(id).style.display = "none";
	}else{
		$(id).style.display = "block";
	}
}

var getResultsContainer = function(text, id){
	var newId = id+"ResultBox";
	var mainText = "<a href='#' onClick='toggle(\""+newId+"\")'>Toggle Result Data</a><br /><div id='"+newId+"' style='display:none'>"+text+"</div>";
	return mainText;
}

var excecuteBenchmarkQuery = function(element, url){
	startTimes[url] = new Date();
	
	//fetch url
	var successHandler = function(o){
		var timeElapsed = getTimeElapsed(startTimes[url]);
		element.innerHTML = "Total Time: "+timeElapsed+"ms | "+getResultsContainer(o.responseText, element.id);
		
		jobname = url.substr(url.lastIndexOf("/")+1, url.length);
		var result = null;
		for(var job in results){
			if(job.name == jobname){
				result=job;
				break;
			}
		}
		if(result===null){
			result = {"name":jobname}	;
			results.push(result);
		}
		if(url.indexOf("MySQL")>0){
			result["MySqlTime"]=timeElapsed;
		}else{
			result["MongoTime"]=timeElapsed;
		}
		updateChart();
	};
	var failureHandler = function(o){
		alert("FAIL! "+o.status + " " + o.statusText);
	};
	
	var request = YAHOO.util.Connect.asyncRequest('GET', url, { success:successHandler, failure:failureHandler }); 
};

var chart = null;
var loadChart = function(){
	YAHOO.widget.Chart.SWFURL = "/static/charts.swf";

	 //--- data

	     var jsonData = new YAHOO.util.DataSource( results );
	     jsonData.responseType = YAHOO.util.DataSource.TYPE_JSARRAY;
	     jsonData.responseSchema =
	     {
	             fields: ["name","MySqlTime","MongoTime"]
	     };
	     
	     var seriesDef =
	    	 [
	    	 	{
	    	 		yField: "MySqlTime",
	    	 		displayName: "MySQL Time"
	    	 	},
	    	 	{
	    	 		yField: "MongoTime",
	    	 		displayName: "Mongo Time"
	    	 	},
	    	 ];

	 //--- chart
	     
	     var styleDef =
	     {
	     	xAxis:{
	     		labelRotation:-90
	     	},
	     	yAxis:{
	     		titleRotation:-90
	     	},
	     	legend:{
	     		display: "bottom"
	     	}

	     }

	     var yAxis = new YAHOO.widget.NumericAxis();
	     yAxis.minimum = 0;
	     yAxis.title = "Time Elapsed (ms)";
	     
	     var xAxis = new YAHOO.widget.CategoryAxis(); 
	     xAxis.title="Query";

	     chart = new YAHOO.widget.ColumnChart( "chart", jsonData,
	     {
	         series:seriesDef,
	         xField: "name",
	         yAxis: yAxis,
	         style: styleDef,
	         //only needed for flash player express install
	         expressInstall: "assets/expressinstall.swf"
	     });
}

var updateChart = function(){
	   chart.refreshData();
}

