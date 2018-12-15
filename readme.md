# PyChat Project

### running project

for sse connections redis is needed:

```bash
sudo apt install redis-server
```

create a virtual environment and install project's requirements using:

```bash
pip install -r requirements.txt
```

__python version 3 should use!__

create a local_params.py in root directory with following variables:

```python
DB_HOST = 'db host'
DB_NAME = 'db name'
DB_USER = 'db user'
DB_PASS = 'db pass'

REDIS_URL = 'redis url'

DEBUG_MODE = True or False
HOST = 'server running host'
```

mysql used for database.

create database using this SQL command:

```mysql
CREATE SCHEMA `me_chat_test` DEFAULT CHARACTER SET utf8 ;
```



run the server using start.py



### using project

first create a account.

login and use create a room or join room button get connected using room name.

in room creation first, enter room's name that you want then share the room's name with another user and waiting for another user to join.
after that, using the start session button (red button) start the webrtc connection.

when you want to join a room, using the join a room button and enter the name of the room and join

### project code explanation

the flask framework is used for writing the web application and for SEE connections, flask_sse used.

users send and receive its signals using a sse connection multiplexed by room name.

for example the user a want's a room with the user b.

firstly the user a creates a room with an arbitrary name and share it with the user b.

when the user a press the create button following function is called:

```javascript
function createRoomBtn() {
        console.log('create room called');
        var room_name = document.querySelector('#create_roomName').value;
        var stream_url = "{{ url_for('sse.stream') }}" + "?channel=" + room_name;
        sse_connection = new EventSource(stream_url);
        sse_connection.addEventListener('join', function (event) {
            var data = JSON.parse(event.data);
            notif("create", data.username + " joined", "alert");
            if (data.username !== "{{ user.username }}") {
                document.querySelector('#session_btn').disabled = false;
            }
        }, null);

        sse_connection.addEventListener('answer', function (event) {
            notif("create", 'answer received', "alert");
            var data = JSON.parse(event.data);
            rtc_connection.setRemoteDescription(new RTCSessionDescription(data.answer));
        }, false);

        joinAnnouncement(room_name);
    }
```



in this function, the room name sends to the server, create an SSE connection that listens for the answer and joins messages.
the answer message is used for webrtc connection and join is used to notifying the user when another user joined.

every room has its owned channel in SSE stream and room's user get messages using this channel.

the jointAnnouncement function is used to notify other members when a new user joined the room.

```javascript
function joinAnnouncement(room_name) {
        var xhr = new XMLHttpRequest();
        xhr.open('POST', "{{ url_for('join_room') }}");
        xhr.onload = function () {
            if (this.status === 200) {
                console.log('join announcement send');
            }
        };
        xhr.send(JSON.stringify({username: "{{ user.username }}", room: room_name}));
    }
```

using xhr this function sends a join message to other members.

the view that handles join requests is:

```python
@App.route('/join_room', methods=['POST'])
@login_required
def join_room():
    data = loads(request.data)
    sse.publish({'username': data.get('username')}, type='join', channel=data.get('room'))
    return Response('ok', status=200)
```

this function gives a username and publishes to other users using sse.publish().

other views that write for sending another kind of messages are like the mentioned view.

now the user b gives the room name and join to it.

when the user enters the room name and click the join button following function is called.

```javascript
function joinRoomBtn() {
        console.log('join room called');
        var room_name = document.querySelector('#join_roomName').value;
        var stream_url = "{{ url_for('sse.stream') }}" + "?channel=" + room_name;
        sse_connection = new EventSource(stream_url);
        rtc_connection = new RTCPeerConnection(configuration);

        rtc_connection.onicecandidate = function (event) {
            if (event.candidate) {
                notif('join', 'onicecandidate called', 'alert');
                var xhr = new XMLHttpRequest();
                xhr.open('POST', "{{ url_for('send_candidate') }}");
                xhr.send(JSON.stringify({candidate: event.candidate, room: room_name}));
            }
        };

        sse_connection.addEventListener('join', function (event) {
            var data = JSON.parse(event.data);
            notif("join", data.username + " joined", "alert");
        }, null);

        joinAnnouncement(room_name);
        sse_connection.addEventListener('offer', function (event) {
            notif("join", 'offer request received', "alert");

            var data = JSON.parse(event.data);
            rtc_connection.setRemoteDescription(new RTCSessionDescription((data.offer)));

            rtc_connection.createAnswer().then(function (answer) {
                rtc_connection.setLocalDescription(answer);
                var xhr = new XMLHttpRequest();
                xhr.open('POST', "{{ url_for('send_answer') }}");
                xhr.onload = function () {
                    if (this.status === 200) {
                        notif("join", 'answer request send', "alert");
                    }
                };
                xhr.send(JSON.stringify({answer: answer, room: room_name}));
            }, null)
        }, false);
```

in this function, SSE and RTC connection is created.
in addition to joining messages this user receives the offer messages and after set rtc's remote description sends an answer to offerer user and connection is established between two users.

also, user state his presence in the room using the joinAnnouncement function that already mentioned.

when all users joined the room the room creator press start session button (that's now actives) and using sse all signals send and receives.

when the user presses the start session button following function is called:

```javascript
function startSession(room_name) {
        console.log('session started');
        notif("create", "session started", "alert");
        rtc_connection = new RTCPeerConnection(configuration);

        rtc_connection.onicecandidate = function (event) {
            if (event.candidate) {
                notif('create', 'onicecandidate called', 'alert');
                var xhr = new XMLHttpRequest();
                xhr.open('POST', "{{ url_for('send_candidate') }}");
                xhr.send(JSON.stringify({candidate: event.candidate, room: room_name}));
            }
        };

        rtc_connection.createOffer().then(function (offer) {
            var xhr = new XMLHttpRequest();
            xhr.open('POST', "{{ url_for('send_offer') }}");
            xhr.onload = function () {
                if (this.status === 200) {

                    notif("create", 'offer send successfully', "alert");
                }
            };
            console.log(room_name);
            xhr.send(JSON.stringify({room: room_name, offer: offer}));
            rtc_connection.setLocalDescription(offer);
        }, null);

        var dataChannelOptions = {
            reliable: true
        };

        console.log('session started');

        dataChannel = rtc_connection.createDataChannel("myDataChannel", dataChannelOptions);

        dataChannel.onerror = function (error) {
            console.log("Error:", error);
        };

        dataChannel.onmessage = function (event) {
            console.log("Got message:");
        };

        dataChannel.onopen = function (event) {
            console.log("send message:");
            dataChannel.send("hi");
        };

    }
```

the start session function sends an offer to another user and its connection is established finally when all messages exchanged.



### Creators

- Amin Hosseini
- Ali Mami Zade
- Amir Mahdi MirFakhar