Video file will contain every action a player makes, but doesn't necessarily contain any information about the mines themselves. In addition, the video file will contain various random data some of which will originate from our server. A truncated video file, when hashed, produces a random number. This is used as the game is being played to generate the position of undetermined mines in real time.

Data sent from server are always signed with our private key. This proves the entropy in their video files came from us.

Server will send seeds and the time they're sent (and signed). Client will use them as starting entropy.

Server can also send a command to demand a ping from the client after a certain amount of time, starting from the first ping up until the game ends. This time can be between ~1s and ~5s, which will ensure that any hacks the client is trying to use will be messed with regularly. In addition, this provides us with a great deal of data about the timings in the video file and how they relate to server time, so that it can be audited.

Pings from the server, aside from the random data, can also contain other information, such as the current server time.

When the client sends pings to the server, it should also send the current video file hash, time, ping number, and the hash of the previous ping. This should aid the server in handling information (I hope), and at the same time, ensures that the video file is not tampered with (despite impossibly low chances).

Client will also use the time the game was started, mouse movements shortly before the game is started, and the current random.random(), just as a little extra entropy.

Try to have sources of entropy that are hard to tamper with in real time. For example, cursor movements are hard to tamper with as trying to do so will make them jittery and unrealistic. On the other hand, high resolution time is probably not a good source as it's not very random in the first place and also allows an attacker to modify the position of mines right before a click if they can change a few bits in the time.


