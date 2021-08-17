import 'https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js'
import { Editor } from 'https://cdn.skypack.dev/@tiptap/core?min'
import StarterKit from 'https://cdn.skypack.dev/@tiptap/starter-kit?min'
import '../node_modules/js-sha256/build/sha256.min.js'
import './jquery.cookie.js'
import { adress_api } from './config.js'


var hash = sha256.create();
var access_token = "";
var token_type = "bearer";
var item_id = null;
var item_created = ""
var item_name = ""


$.ajaxSetup({
	headers: { 
		"Accept": "application/json",
	}
});


function html_to_text(data, last_n=true) {
	data = data.replace(/<style([\s\S]*?)<\/style>/gi, '');
	data = data.replace(/<script([\s\S]*?)<\/script>/gi, '');
	data = data.replace(/<\/div>/ig, '\n');
	data = data.replace(/<\/li>/ig, '\n');
	data = data.replace(/<li>/ig, '  * ');
	data = data.replace(/<\/ul>/ig, '\n');
	data = data.replace(/<p>/ig, '');
	data = data.replace(/<\/p>/ig, '\n');
	data = data.replace(/<br\s*[\/]?>/gi, '\n');
	data = data.replace(/<[^>]+>/ig, '');
	if (last_n == true) {
		data = data.replace(/\n+$/m, '');
	}
	else if (data.slice(-1) == '\n') {
		data = data.slice(0, -1);
	}
	data = data.replace(/\\n/ig, '\n');
	return data;
}

function text_to_html(data) {
	data = data.replace(/\n/gi, '</p><p>');
	data = data.replace(/\t/gi, '    ');
	data = '<p>' + data + '</p>';
	return data
}

function get_info(res) {
	var info = "";
	if (res != null) {info = info + "<p>success = " + String(res.success) + "</p>";}
	info = info + "<p>item_id = " + item_id + "</p>";
	info = info + "<p>created = " + item_created + "</p>";
	if (res != null) {info = info + "<p>time = " + res.time_query + "</p>";}
	return info;
}

function get_info_success(res) {
	var info = "";
	if (res != null) {info = info + "<p>success = " + String(res.success) + "</p>";}
	return info;
}


const editor_thema = new Editor({
	element: document.querySelector('.thema'),
	extensions: [StarterKit,],
	autofocus: true,
	editable: true,
	injectCSS: false,
})

const editor_text = new Editor({
	element: document.querySelector('.text'),
	extensions: [StarterKit,],
	content: '',
	autofocus: false,
	editable: true,
	injectCSS: false,
})
	
const editor_next = new Editor({
	element: document.querySelector('.next'),
	extensions: [StarterKit,],
	content: '',
	autofocus: false,
	editable: true,
	injectCSS: false,
})
	
const editor_liner = new Editor({
	element: document.querySelector('.liner'),
	extensions: [StarterKit,],
	content: '',
	autofocus: false,
	editable: true,
	injectCSS: false,
})


$(document).ready(function() {
	access_token = $.cookie('access_token');
	token_type = $.cookie('token_type'); console.log("Authorization: " + token_type + " " + access_token);
	item_id = $.cookie('item_id'); console.log('item_id=' + item_id);
	item_created = $.cookie('item_created'); console.log('item_created=' + item_created);
	item_name = $.cookie('item_name'); console.log('item_name=' + item_name);
	
	if (access_token != null && token_type != null) {
		document.getElementById("generator").style.display = 'block';
		document.getElementById("err_auth").style.display = 'none';
		$.ajaxSetup({
			headers: { 
			"Accept": "application/json",
			"Authorization": token_type + " " + access_token,
			}
		});
	}
	if (item_id != null && item_name != null && item_created != null) {
		document.getElementById("result").innerHTML = get_info(null);
		editor_thema.commands.setContent(text_to_html(item_name));
		$.ajax({
			method: "GET",
			url: adress_api + "/api/text/" + item_id,
			contentType: "application/json; charset=utf-8",
			dataType: "json",
			crossDomain: true,
			success: function(res) {
				console.log(res);
				if (res.text != null) {
					editor_text.commands.setContent(text_to_html(res.text));
				}
			},
			error: function(er) {console.log(er);},
		});
	}
	
	$('button.text_create').click(function(e) {
		e.preventDefault();  // Stop form from sending request to server
		var btn = $(this);
		$.ajax({
			method: "GET",
			url: adress_api + "/api/text/new",
			contentType: "application/json; charset=utf-8",
			dataType: "json",
			crossDomain: true,
			data: {
				"name": html_to_text(editor_thema.getHTML()),
			},
			success: function(res) {
				console.log(res);
				item_id = res.id; $.cookie('item_id', item_id);
				item_created = res.created; $.cookie('item_created', item_created);
				item_name = html_to_text(editor_thema.getHTML()); $.cookie('item_name', item_name);
				document.getElementById("result").innerHTML = get_info(null);
			},
			error: function(er) {console.log(er);},
		});
	});

	$('button.text_next').click(function(e) {
		e.preventDefault();  // Stop form from sending request to server
		var btn = $(this);
		$.ajax({
			method: "GET",
			url: adress_api + "/api/text/next/" + item_id,
			contentType: "application/json; charset=utf-8",
			dataType: "json",
			crossDomain: true,
			data: {
				"text": html_to_text(editor_text.getHTML(), false),
				"text_next": html_to_text(editor_next.getHTML(), false),
				"liner": html_to_text(editor_liner.getHTML()),
				"text_type": document.getElementById("text_type").value,
			},
			success: function(res) {
				console.log(res);
				if (res.success == true) {
					editor_text.commands.setContent(text_to_html(res.text));
					editor_next.commands.setContent(text_to_html(res.next));
					editor_liner.commands.setContent("");
					document.getElementById("result").innerHTML = get_info(res);
				}
				else {
					document.getElementById("result").innerHTML = get_info_success(res);
				}
			},
			error: function(er) {console.log(er);},
		});
	});
		
	$('button.text_update').click(function(e) {
		e.preventDefault();  // Stop form from sending request to server
		var btn = $(this);
		$.ajax({
			method: "GET",
			url: adress_api + "/api/text/update/" + item_id,
			contentType: "application/json; charset=utf-8",
			dataType: "json",
			crossDomain: true,
			data: {
				"text": html_to_text(editor_text.getHTML(), false),
				"text_next": html_to_text(editor_next.getHTML(), false),
				"liner": html_to_text(editor_liner.getHTML()),
				"text_type": document.getElementById("text_type").value,
			},
			success: function(res) {
				console.log(res);
				if (res.success == true) {
					editor_next.commands.setContent(text_to_html(res.next));
					document.getElementById("result").innerHTML = get_info(res);
				}
				else {
					document.getElementById("result").innerHTML = get_info_success(res);
				}
			},
			error: function(er) {console.log(er);},
		});
	});
		
	$('button.text_finish').click(function(e) {
		e.preventDefault();  // Stop form from sending request to server
		var btn = $(this);
		$.ajax({
			method: "GET",
			url: adress_api + "/api/text/finish/" + item_id,
			contentType: "application/json; charset=utf-8",
			dataType: "json",
			crossDomain: true,
			data: {
				"text": html_to_text(editor_text.getHTML(), false),
				"text_next": html_to_text(editor_next.getHTML(), false),
				"liner": html_to_text(editor_liner.getHTML()),
				"text_type": "No style",
			},
			success: function(res) {
				console.log(res);
				if (res.success == true) {
					editor_text.commands.setContent(text_to_html(res.text));
					editor_next.commands.setContent("");
					editor_liner.commands.setContent("");
					item_id = null; $.removeCookie('item_id');
					item_created = ""; $.removeCookie('item_created');
					item_name = null; $.removeCookie('item_name');
					//editor_thema.commands.setContent("");
					document.getElementById("result").innerHTML = "";
				}
			},
			error: function(er) {console.log(er);},
		});
	});
	
	$('button.login').click(function(e) {
		e.preventDefault();  // Stop form from sending request to server
		
		$.ajaxSetup({
			headers: { 
				"Accept": "application/json",
			}
		});
		
		hash.update(document.getElementById("password").value);
		console.log("hash: " + hash.hex());
		$.ajax({
			method: "POST",
			url: adress_api + "/login",
			dataType: "json",
			data: {
				"username": document.getElementById("login").value,
				"password": document.getElementById("password").value,
			},
			success: function(res) {
				console.log(res);
				document.getElementById("generator").style.display = 'block';
				document.getElementById("err_auth").style.display = 'none';
				access_token = res.access_token; $.cookie('access_token', access_token);
				token_type = res.token_type; $.cookie('token_type', token_type);
				$.ajaxSetup({
					headers: { 
					"Accept": "application/json",
					"Authorization": token_type + " " + access_token,
					}
				});
			},
			error: function(er) {
				console.log(er);
				document.getElementById("err_auth").style.display = 'block';
			},
		});
	});
	
	$('button.logout').click(function(e) {
		e.preventDefault();  // Stop form from sending request to server
		access_token = ""; $.removeCookie('access_token');
		token_type = "bearer"; $.removeCookie('token_type');
		item_id = null; $.removeCookie('item_id');
		item_created = ""; $.removeCookie('item_created');
		item_name = ""; $.removeCookie('item_name');
		document.getElementById("result").innerHTML = "";
		document.getElementById("generator").style.display = 'none';
		document.getElementById("err_auth").style.display = 'none';
	});
});
