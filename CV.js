function closest_diploma_skill(el) {
  /*Return the (grand grand ...) parent element of class diploma or skill, except if a full_text is in the way, in which case return null*/
  while (el) {
    if(el.className.match(/(?:^|\s)(full_text)(?!\S)/)) return;
    if (el.className.match(/(?:^|\s)(diploma|skill)(?!\S)/)) return el;
    el = el.parentNode;
  }
}
function removeListeners(el){
  var new_element = el.cloneNode(true);
  el.parentNode.replaceChild(new_element, el);
  return new_element;
}
function makeCollapsed(target){
  //Change the section's class
  if (target.className.match(/(?:^|\s)(collapsed)(?!\S)/)) return;
  if (target.className.match(/(?:^|\s)(hidden)(?!\S)/)){
    target.className = target.className.replace( /(?:^|\s)(hidden)(?!\S)/g , ' collapsed' )
  }else{
    target.className = target.className+" collapsed";
  }
  //Change the menu item's class and behaviour
  var item = document.getElementById("toggling_list_item_"+target.id);
  item.className = "list-group-item list-group-item-info";
  item = removeListeners(item);
  item.addEventListener('click', makeTargetFull);
}
function makeInvisible(target){
  //Change the section's class
  if (target.className.match(/(?:^|\s)(hidden)(?!\S)/)) return;
  if (target.className.match(/(?:^|\s)(collapsed)(?!\S)/)){
    target.className = target.className.replace( /(?:^|\s)(collapsed)(?!\S)/g , ' hidden' )
  }else{
    target.className = target.className+" hidden";
  }
  //Change the menu item's class and behaviour
  var item = document.getElementById("toggling_list_item_"+target.id);
  item.className = "list-group-item list-group-item-danger";
  item = removeListeners(item);
  item.addEventListener('click', makeTargetCollapsed);
}
function makeFull(target){
  console.log("makeTargetFull called on");
  console.log(target);
  //Change the section's class
  if (target.className.match(/(?:^|\s)(hidden)(?!\S)/)){
    target.className = target.className.replace( /(?:^|\s)(hidden)(?!\S)/g , '' )
  }
  if (target.className.match(/(?:^|\s)(collapsed)(?!\S)/)){
    target.className = target.className.replace( /(?:^|\s)(collapsed)(?!\S)/g , '' )
  }
  //Change the menu item's class and behaviour
  var item = document.getElementById("toggling_list_item_"+target.id);
  item.className = "list-group-item list-group-item-success";
  item = removeListeners(item);
  item.addEventListener('click', makeTargetInvisible);
}
function toggleCollapse(e){
  e = e || window.event;
  var target = e.target || e.srcElement;
  target = closest_diploma_skill(target);
  if(target){
    if (target.className.match(/(?:^|\s)(collapsed)(?!\S)/)){
      makeFull(target)
    }else{
      makeCollapsed(target)
    }
  }
  console.log("toggleCollapse called !")
  console.log(target)
}
function findIdFromLink(e){
  e = e || window.event;
  var el = e.target || e.srcElement;
  console.log("Find id from Link");
  console.log(el);
  return el.dataset.target.substring(1);
}
function makeTargetCollapsed(e){
   target = document.getElementById(findIdFromLink(e));
  makeCollapsed(target);
}
function makeTargetInvisible(e){
  target = document.getElementById(findIdFromLink(e));
  makeInvisible(target);
}
function makeTargetFull(e){
  target = document.getElementById(findIdFromLink(e));
  if(target){/*can be null if a link with no data-target attribute is clicked in the text of an CV element.*/
    makeFull(target);
  }
}
function addListenerToLinks(el){
  for (var i = 0; i < el.childNodes.length; i++) {
     addListenerToLinks(el.childNodes[i]);
  }
  if(el.tagName == "A"){
    el.addEventListener('click', makeTargetFull);
  }
}
function allCVElements(){
  return Array.prototype.slice.call(document.getElementsByClassName("diploma")).concat(Array.prototype.slice.call(document.getElementsByClassName("skill")));
}
function makeAllFull(){
  /*I guess map exists in javascript, but I don't know the syntax and don't have internet right now to check. FIXME (later).*/
  var elements = allCVElements();
  for (var i = 0; i < elements.length; i++) {
    makeFull(elements[i]);
  }
}
function makeAllCollapsed(){
  /*I guess map exists in javascript, but I don't know the syntax and don't have internet right now to check. FIXME (later).*/
  var elements = allCVElements();
  for (var i = 0; i < elements.length; i++) {
    makeCollapsed(elements[i]);
  }
}
function makeAllInvisible(){
  /*I guess map exists in javascript, but I don't know the syntax and don't have internet right now to check. FIXME (later).*/
  var elements = allCVElements();
  for (var i = 0; i < elements.length; i++) {
    makeInvisible(elements[i]);
  }
}

/*QueryString is copied from http://stackoverflow.com/questions/979975/how-to-get-the-value-from-url-parameter */
var QueryString = function () {
  // This function is anonymous, is executed immediately and
  // the return value is assigned to QueryString!
  var query_string = {};
  var query = window.location.search.substring(1);
  var vars = query.split("&");
  for (var i=0;i<vars.length;i++) {
    var pair = vars[i].split("=");
    pair[1] = decodeURIComponent(pair[1]);
    	// If first entry with this name
    if (typeof query_string[pair[0]] === "undefined") {
      query_string[pair[0]] = pair[1];
    	// If second entry with this name
    } else if (typeof query_string[pair[0]] === "string") {
      var arr = [ query_string[pair[0]], pair[1] ];
      query_string[pair[0]] = arr;
    	// If third or later entry with this name
    } else {
      query_string[pair[0]].push(pair[1]);
    }
  }
    return query_string;
} ();
window.onload = function()
{
  var list_full = QueryString.full || "";
  list_full = list_full.split(",");
  console.log(list_full)
  var list_collapsed = QueryString.collapsed || "";
  list_collapsed = list_collapsed.split(",");
  console.log(list_collapsed)

  var btn = document.getElementById("full_all");
  btn.addEventListener( 'click', makeAllFull );
  var btn = document.getElementById("collapse_all");
  btn.addEventListener( 'click', makeAllCollapsed );
  var btn = document.getElementById("hide_all");
  btn.addEventListener( 'click', makeAllInvisible );

  var list = document.getElementById("toggling_list");
  var elements = allCVElements();
  for (var i = 0; i < elements.length; i++) {
    elements[i].addEventListener( 'click' , toggleCollapse );
    addListenerToLinks(elements[i]);

    link = document.createElement("a");
    link.id = "toggling_list_item_"+elements[i].id;
    link.dataset.target = '#'+elements[i].id; /*No href, cause we don't want to go away when we click*/
    //link.href="#";//+elements[i].id;
    link.className="list-group-item";
    link.textContent=elements[i].getAttribute("data-shortname");

    list.appendChild(link);


    if(list_full.indexOf(elements[i].id) != -1){
      makeFull(elements[i]);
    }else if(list_collapsed.indexOf(elements[i].id) != -1){
      makeCollapsed(elements[i]);
    }else{
      if(list_full[0] == "" && list_collapsed[0] == ""){
        makeCollapsed(elements[i]);
      }else{
        makeInvisible(elements[i]);
      }
    }
  }
}
