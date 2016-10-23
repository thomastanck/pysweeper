PySweeper Video File Format v0.0 (mega unstable)
====

## Introduction

The video file is a record of a player's actions and the state of a Minesweeper board which allows us to view a replay of a game. In PySweeper, one of our cheat prevention techniques is to include a subset of the video file containing some of the player's actions in the generation of the board itself! This first eliminates the possibility of the UPK (Unfair Prior Knowledge) cheats and also makes it extremely difficult to tamper with the video file, bordering on impossible.

## Internals

The video file is a list of tuples encoded as python literals and then compressed with zlib.

Python literal encoding and decoding are done using the standard python module 'ast'.

Compression is done using the standard python module 'zlib'.

## Commands

Each tuple can be interpreted as a command or action, which is performed by either the player or the client. The video file is then a record of all actions performed by either player or client in a strictly sequential format. The state of the client at aby point in time should be completely determinable from a truncated list of such commands. (TODO: is there any benefit from a non sequential format such as a graph?)

The first element of the tuple is the "command name", with the remaining elements as additional parameters to the command. The following commands are used:

* COMMAND_NAME arg1 arg2 ... --> ("COMMAND_NAME", arg1, arg2, ...)

### List of commands

Metadata:

* VERSION      version_string
* VIDEOVERSION version_string
* TIME         seconds_since_unix_epoch
* SECONDS      rounded_seconds_since_unix_epoch

* DISPLAY            x y width height
* PANEL              x y width height
* MINECOUNTER        x y width height
* FACEBUTTON         x y width height
* TIMER              x y width height
* BOARD              x y width height

* BORDER_TOP_LEFT    x y width height
* BORDER_TOP         x y width height
* BORDER_TOP_RIGHT   x y width height
* BORDER_PANEL_LEFT  x y width height
* BORDER_PANEL_RIGHT x y width height
* BORDER_MID_LEFT    x y width height
* BORDER_MID         x y width height
* BORDER_MID_RIGHT   x y width height
* BORDER_LEFT        x y width height
* BORDER_RIGHT       x y width height
* BORDER_BOT_LEFT    x y width height
* BORDER_BOT         x y width height
* BORDER_BOT_RIGHT   x y width height

* TILESIZE     width height
* BOARDSIZE    rows cols

* GAMEMODE     string
* GAMEOPTIONS  string
# NUMMINES     num_mines

-- ^ implemented up to here

* PINGVERSION  version_string
* PINGUP       time servername
* PINGDOWN     time servername response response_signature

* SERVERVERSION     version_string
* SERVERTIME        time
* SERVERSEED        randomness
* RESPONSESIGNATURE signature_of_response
* VIDEOSIGNATURE    signature_of_video_file

-- ^ not implemented yet

* ADDSEED string

-- ^ implemented

Player actions:

* MOVE      time x y
* LMBDOWN   time x y
* RMBDOWN   time x y
* LMBUP     time x y
* RMBUP     time x y
* STARTGAME time x y
* DEPRESS   time row col
* UNDEPRESS time row col
* OPEN      time row col
* FLAG      time row col
* UNFLAG    time row col
* CHORD     time row col

Client actions:

* GENERATE time row col is_mine
* REVEAL   time row col (number|tile_type)
* COUNTER  mines_remaining
* TIMER    seconds_since_start_of_game
* WIN      time
* LOSE     time

### Examples

Metadata:

* VERSION version_string (e.g. "PySweeper v0.0")
* TIME seconds_since_unix_epoch (e.g. 1476939624.215525)
* PINGVERSION version_string (e.g. PySweeper Ping Protocol 0.2dev0)
* PINGUP time servername (e.g. 1476939624.215525 "ping.pysweeper.com")
* PINGDOWN time servername response response_signature (e.g. 1476939624.215525 "ping.pysweeper.com" {"recv_time": 3728...,"other_keys":other_values,...} "keHi829-HhiWrxXIB")
* SERVERVERSION version_string (e.g. PySweeper Ping Protocol 0.2dev0)
* SERVERTIME time (e.g. 1476939624.215525)
* SERVERSEED randomness (e.g. "keHi829-HhiWrxXIB...")
* ADDSEED string (e.g. "(MOVE, 3, 10)")

Player actions:

* MOVE time y x (e.g. 1476939624.215525 65 224)

## The RNG (Random Number Generator)

In PySweeper, the video stream and the state of the game are exactly the same. This includes the state of the RNG! As part of our cheat prevention, we must include some subset of the player's actions, a checksum of the board state, and the client/server interaction within the state of the RNG.

We record this in the video file within "ADDSEED" commands. Every "ADDSEED" command appends the string in arg1 to the state of the RNG. This state is hashed using the SHA-512 algorithm and this number is used as the random number generator's output.

By expressing a probability in a fraction, then taking the remainder of the random number after dividing by the denominator and checking if the remainder is less than the numerator, we can sample a True/False value using at probability given.

