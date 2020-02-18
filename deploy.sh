#!/bin/bash

git_repo="https://github.com/s0lst1ce/Botanist.git"
name="Botanist"
#home_url="https://github.com/s0lst1ce/Botanist"

helpFunction(){
    echo ""
    echo "Usage: $0 TOKEN"
    echo "  -h shows this help message"
    echo "  -n name of the bot. Default is Botanist"
    echo "  -u home url for the bot"
    echo "  -p set the prefix the bot should listen to"
    exit 0
}

[ $# -eq 0 ] && helpFunction

#parsing options
while getopts ":hn:u:p:" option; do
    case $option in
        h | help )
            helpFunction;;

        n | name )
            name=$OPTARG;;

        u )
            home_url=$OPTARG;;

        p )
            prefix=$OPTARG;;

        \? )
            echo "Invalid option -$OPTARG"
            helpFunction;;

        \: ) echo "Missing argument for -$OPTARG"
            helpFunction;;

        \- ) echo "Long options are not yet supported!";;

    esac
    #shift
done

#installing the bot
echo "Downloading bot into $name."
git clone $git_repo $name &> /dev/null

#setting TOKEN as env var
token=$1
if [[ ! -z $DISCORD_TOKEN ]]; then
    echo "Environement variable DISCORD_TOKEN already exists! Please clear it before proceeding to installation of the bot."
    #exit 1
fi

#configuring the bot
echo "Applying configuration."
settings_path="$name/settings.py"

if [[ ! -z $prefix ]]; then
    echo "yup"
    sed -i "s/PREFIX\(.*\)/PREFIX = '$prefix'/" $settings_path #-i is not standard POSIX, merely GNU sed
fi

if [[ ! -z $home_url ]]; then
    sed -i "s/WEBSITE\(.*\)/WEBSITE = '$home_url'/" $settings_path
fi
echo -e "DISCORD_TOKEN=$token\n" >> ~/bashrc_testing

if [[ -z command -v python3 ]]; then
    echo "Python3 is a required dependency of the bot. If you are sure you have it make sure it points to python3"
    exit 1
fi

echo "Making python dpy virtual environement..."
python3 -m venv $name/dpy
source $name/dpy/bin/activate

echo "Installing dependencies."
python3 -m pip install -r $name/requirements.txt
deactivate

echo "Finished installing $name. To start it run: source $name/dpy/bin/activate && python3 $name/main.py"
exit 0