console.log('check')
$(document).ready(function() {
    const button = $('<button>', {
        text: 'Voice Recognition',
        class: 'button',
        id: 'start-button'
    });

    const outputDiv = $('<div>', {
        class: 'output',
        id: 'output'
    });

    
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        alert('Your browser does not support speech recognition. Please try Google Chrome.');
        return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();

    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';
    recognition.onstart = function() {
        button.text('Listening...');
        button.prop('disabled', true);
    };

    recognition.onspeechend = function() {
        recognition.stop();
        button.text('Start Speaking');
        button.prop('disabled', false);
    };

    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        console.log(transcript)
        outputDiv.text('You said: ' + transcript);
        frappe.call({
            method: 'voice_recognition.voice_recognition.customization.speech_recognization.utility.identify_voice',
            args: {
                speech_text: transcript,
                url: window.location.href
            },
            callback: function(response) {
                console.log(response);
                if(response.message[0] == 'create new'){
                    frappe.new_doc(response.message[1], {}, function(doc) {   
                        setTimeout(function() {
                            console.log(cur_dialog)
                            frappe.set_route('Form', response.message[1], cur_dialog.doc.name);
                        }, 1000);
                    });
                    restartRecognition();
                } else if (response.message[0] == 'child'){
                    cur_frm.add_child(response.message[1]);
                    restartRecognition();
                    // frappe.model.set_value(child.doctype, child.name, 'item_code', item.item_code);
                }
                else if (response.message.length == 2){
                    console.log(cur_frm.doc)
                    if (response.message[1] == 'tick'){
                        cur_frm.set_value(response.message[0], 1);
                    }else if (response.message[1] == 'untick'){
                        cur_frm.set_value(response.message[0], 0);
                    }else{
                        cur_frm.set_value(response.message[0], response.message[1]);
                    }
                    cur_frm.refresh_field(response.message[0]);
                restartRecognition();
                }else if(response.message == 'save'){
                    cur_frm.save_or_update();
                    restartRecognition();
                }else if (response.message.length != 2){
                    frappe.set_route(response.message);
                    restartRecognition();
                }else{
                    restartRecognition();
                }
            },
            error: function(err) {
                console.log(err);
                alert('Error occurred: ' + err.message);
                restartRecognition();
            }
        });
    };


    recognition.onerror = function(event) {
        alert('Error occurred in recognition: ' + event.error);
        button.text('Start Listening');
        button.prop('disabled', false);0
        restartRecognition();
    };

    button.click(function() {   
        event.preventDefault();
        recognition.start();
           
    });

    // Function to restart recognition
    function restartRecognition() {
        button.text('Listening...');
        button.prop('disabled', true);
        recognition.start();
    }


    button.css({
        'background-color': 'black', // Green
        'border': 'none',
        'color': 'white',
        'text-align': 'center',
        'text-decoration': 'none',
        'display': 'inline-block',
        'font-size': '16px',
        'margin': '4px 2px',
        'cursor': 'pointer',
        'border-radius': '12px',
        'transition': 'background-color 0.3s, transform 0.3s'
    });

    button.hover(
        function() {
            $(this).css({
                'background-color': '#45a049',
                'transform': 'scale(1.05)'
            });
        }, function() {
            $(this).css({
                'background-color': '#4CAF50',
                'transform': 'scale(1)'
            });
        }
    );

    $('.form-inline.fill-width.justify-content-end').append(button);
});
