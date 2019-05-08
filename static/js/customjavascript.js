function hoverTab(tabData){
  tabData.style.backgroundPosition = " 0% -50px";
  tabData.style.lineHeight = "24px";
}

function outTab(tabData){
  tabData.style.backgroundPosition = " 0% -25px";
}

function executeTab(tabData){
  tabData.className = "tabactive";
  tabData.style.backgroundPosition = " 0% -0px";
  tabData.onmouseover=function(){};
  tabData.onmouseout=function(){};
}

function showTabData(idForDisplay){
  var tabnewest = document.getElementById('tab-newest');
  var tabMostview = document.getElementById('tab-mostview');
  var tabTrending = document.getElementById('tab-trending');

  var liNewesttab = document.getElementById('liNewesttab');
  var liMostViewtab = document.getElementById('liMostViewtab');
  var liTrendingtab = document.getElementById('liTrendingtab');

  tabnewest.style.display = "none";
  tabMostview.style.display = "none";
  tabTrending.style.display = "none";

  liNewesttab.className = "";
  liMostViewtab.className = "";
  liTrendingtab.className = "";

  liNewesttab.style.backgroundPosition = " 0% -25px";
  liMostViewtab.style.backgroundPosition = " 0% -25px";
  liTrendingtab.style.backgroundPosition = " 0% -25px";

  liNewesttab.onmouseover = function () { hoverTab(this); }
  liMostViewtab.onmouseover = function () { hoverTab(this); }
  liTrendingtab.onmouseover = function () { hoverTab(this); }

  liNewesttab.onmouseout = function () { outTab(this); }
  liMostViewtab.onmouseout = function () { outTab(this); }
  liTrendingtab.onmouseout = function () { outTab(this); }

  if (idForDisplay == "mostview") {
      tabMostview.style.display = "block";
      executeTab(liMostViewtab);
  }
      else if (idForDisplay == "newest") {
          tabnewest.style.display = "block";
          executeTab(liNewesttab);
      }
      else if (idForDisplay == "trending") {
          tabTrending.style.display = "block";
          executeTab(liTrendingtab);
      }
}
