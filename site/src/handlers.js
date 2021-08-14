import 'https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js'
import { Editor } from 'https://cdn.skypack.dev/@tiptap/core?min'
import StarterKit from 'https://cdn.skypack.dev/@tiptap/starter-kit?min'
import '../node_modules/js-sha256/build/sha256.min.js'


var hash = sha256.create();


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


const adress_api = "http://127.0.0.1:8000";
var access_token = "";
var token_type = "bearer";
var item_id = null;


$.ajaxSetup({
	headers: { 
		"Accept": "application/json",
		"Authorization": token_type + " " + access_token,
	}
});


$(document).ready(function() {
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
				"name": editor_thema.getHTML(),
			},
			success: function(res) {
				console.log(res);
				item_id = res.id;
				var info = "<p>item_id = " + item_id + "</p><p>created = " + res.created + "</p>";
				document.getElementById("result").innerHTML = info;
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
				"text": editor_text.getHTML(),
				"text_next": editor_next.getHTML(),
				"liner": editor_liner.getHTML(),
				"text_type": "No style",
			},
			success: function(res) {
				console.log(res);
				if (res.success == true) {
					editor_text.commands.setContent(res.text);
					editor_next.commands.setContent(res.next);
					editor_liner.commands.setContent("");
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
				"text": editor_text.getHTML(),
				"text_next": editor_next.getHTML(),
				"liner": editor_liner.getHTML(),
				"text_type": "No style",
			},
			success: function(res) {
				console.log(res);
				if (res.success == true) {
					editor_next.commands.setContent(res.next);
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
				"text": editor_text.getHTML(),
				"text_next": editor_next.getHTML(),
				"liner": editor_liner.getHTML(),
				"text_type": "No style",
			},
			success: function(res) {
				console.log(res);
				if (res.success == true) {
					editor_text.commands.setContent(res.text);
					editor_next.commands.setContent("");
					editor_liner.commands.setContent("");
					item_id = null;
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
				access_token = res.access_token;
				token_type = res.token_type;
			},
			error: function(er) {console.log(er);},
		});
	});
	
	$('button.logout').click(function(e) {
		e.preventDefault();  // Stop form from sending request to server
		access_token = "";
		token_type = "bearer";
		item_id = null;
		document.getElementById("generator").style.display = 'none';
	});
});
