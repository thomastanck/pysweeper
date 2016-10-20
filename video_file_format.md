# Introduction

The video file is a record of a player's actions and the state of a Minesweeper board which allows us to view a replay of a game. In PySweeper, one of our cheat prevention techniques is to include a subset of the video file containing some of the player's actions in the generation of the board itself! This first eliminates the possibility of the UPK (Unfair Prior Knowledge) cheats and also makes it extremely difficult to tanper with the video file, bordering on impossible.

# Internals

The video file is a compressed json file which contains a list of tuples (json does not have tuples, so they'll be lists too).

## Commands

Each tuple can be interpreted as a command or action, which is performed by either the player or the client. The video file is then a record of all actions performed by either player or client in a strictly sequential format. The state of the client at aby point in time should be completely determinable from a truncated list of such commands. (TODO: is there any benefit from a non sequential format such as a graph?)

The first element of the tuple is the "command name", with the remaining elements as additional parameters to the command. The following commands are used:

* COMMAND_NAME arg1 arg2 ... --> ("COMMAND_NAME", arg1, arg2, ...)

Metadata:

* VERSION version_string (e.g. "PySweeper 0.1dev0")
* TIME seconds_since_unix_epoch (e.g. 1476939624.215525)
* PINGVERSION version_string (e.g. PySweeper Ping Protocol 0.2dev0)
* PINGUP time servername (e.g 1476939624.215525 "ping.pysweeper.com")
* PINGDOWN time servername response response_signature (e.g. 1476939624.215525 "ping.pysweeper.com" {"recv_time": 3728...,"other_keys":other_values,...} "keHi829-HhiWrxXIB")
* SERVERVERSION version_string (e.g. PySweeper Ping Protocol 0.2dev0)
* SERVERTIME time (e.g. 1476939624.215525)
* SERVERSEED randomness (e.g. "keHi829-HhiWrxXIB...")
* RESPONSESIGNATURE signature_of_response
* VIDEOSIGNATURE signature_of_video_file
* ADDSEED string (e.g. "(MOVE, 3, 10)")

Player actions:

* MOVE time y x (e.g. 1476939624.215525 65 224)
* LMBDOWN time y x
* RMBDOWN time y x
* LMBUP time y x
* RMBUP time y x
* STARTGAME time y x
* OPEN time row col
* FLAG time row col
* UNFLAG time row col
* CHORD time row col

Client actions:

* GENERATE time row col is_mine
* REVEAL time row col (number|tile_type)
* COUNTER mines_remaining
* TIMER seconds_since_start_of_game
* WIN time
* LOSE time