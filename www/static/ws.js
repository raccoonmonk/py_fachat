var input_text_field = document.getElementById("txt_field");
var board = document.getElementById("board");
var roster = document.getElementById("roster");

//RoomTab obj
var roomTab = {
	isActive : true,
	intervalId: undefined,
	title: document.title,
	unreadMess: 0,
	glow: function(toGlow) {
		if (this.isActive)
			return;
		if (toGlow) {
			this.unreadMess++;
			if (!this.intervalId)
				this.intervalId = setInterval(
					function() {
						document.title = ((roomTab.title == document.title) ? 
							("[" + roomTab.unreadMess + "] " + roomTab.title) : roomTab.title);
					}, 1000);
		} else {
			document.title = this.title;
			this.unreadMess = 0;
			clearInterval(this.intervalId);
			this.intervalId = undefined;
		};	
	}
};

//activeness of the tab
window.onfocus = function () {
	roomTab.glow(false);
	roomTab.isActive = true;
};

window.onblur = function () {
	roomTab.glow(false);
	roomTab.isActive = false;
};

if (document.domain == "localhost")
	var url = "ws://localhost:15001/ws/";
else
	var url = "ws://chat-raccoonmonk.rhcloud.com:8000/ws/";
try {
	var room = document.location.pathname.match(/^.*\/room\/(\w+)$/)[1];
} catch (e) {
	window.location = document.location.origin;
};
url += room;
var ws = new WebSocket(url);

input_text_field.onkeypress = function(key) {
	if (key.keyCode == 0x0D) {
		send();
	};
};
send = function(){
	var msg = input_text_field.value;
	if (msg == "")
		return;
	ws.send(msg);
	board.addEntity("You" + ": " + msg);
	input_text_field.value = "";
	input_text_field.focus();
};

input_text_field.focus();

//Creates WebSocket event listeners
if (!ws) {
	board.addEntity("Your web browser does not support WebSockets, sorry");
};
ws.onopen = function(e) {
	board.addEntity("Connection has been established...");
};
ws.onmessage = function(e) {
	//parse json
	var obj = JSON.parse(e.data);
	switch(obj.code){
		case "usr":
			board.addEntity(obj.from + ": " + obj.text);
			roomTab.glow(true);
			break;
		case "srv":
			board.addEntity(obj.text);
			roomTab.glow(true);
			break;
		case "roster":
			roster.update(obj.ext);
			break;
		default:
			break;
	};
};
ws.onclose = function(e) {
	board.addEntity("Socket has been closed...");
};

function escapeHtml(text) {
	// escape html spec chars
	return text.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/(http:\/\/[\S]+\b)/g, '<a href="$1" target="_blank">$1</a>');
};

function getTime() {
	var date = new Date();
	var hh = date.getHours();
	var mm = date.getMinutes();
	var ss = date.getSeconds();
	var str = (hh < 10 ? "0" : "") + hh + 
		(mm < 10 ? ":0" : ":") + mm +
		(ss < 10 ? ":0" : ":") + ss;
	return str;
};

board.addEntity = function(str) {
	// add a record on board
	var p = document.createElement("div");
	p.innerHTML = getTime() + " " + escapeHtml(str);
	this.appendChild(p);
	this.scrollTop = this.scrollHeight - this.clientHeight;
};

roster.update = function(arr){
	this.innerHTML = "";
	for(var i = 0; i < arr.length; i++){
		var p = document.createElement("div");
		p.innerHTML = escapeHtml(arr[i]);
		this.appendChild(p);
	};
};
