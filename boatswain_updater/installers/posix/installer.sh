#  This file is part of Boatswain.
#
#      Boatswain is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      Boatswain is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with Boatswain.  If not, see <https://www.gnu.org/licenses/>.
#
#

#!/usr/bin/env bash

UPDATE_APP_DIR="$1"
ORIGINAL_APP_DIR="$2"
BACKUP_DIR="/tmp/boatswain/backup"

if [ ! -d "$ORIGINAL_APP_DIR" ]
then
  echo "Directory $ORIGINAL_APP_DIR does not exists."
  exit -1
fi

if [ ! -d "$UPDATE_APP_DIR" ]
then
  echo "Directory $UPDATE_APP_DIR does not exists."
  exit -1
fi

if [ ! -d "$BACKUP_DIR" ]
then
  mkdir -p "$BACKUP_DIR"
else
  rm -rf "$BACKUP_DIR/*"
fi

restore() {
  for x in $BACKUP_DIR/* $BACKUP_DIR/.[!.]* $BACKUP_DIR/..?*; do
    if [ -e "$x" ]; then mv -- "$x" $ORIGINAL_APP_DIR/; fi
  done
}

# Move things from application directory to backup folder
for x in $ORIGINAL_APP_DIR/* $ORIGINAL_APP_DIR/.[!.]* $ORIGINAL_APP_DIR/..?*; do
  if [ -e "$x" ]; then mv -- "$x" $BACKUP_DIR/; fi
  if [ $? -ne 0 ]; then
    echo "Unnable to move file $x from $ORIGINAL_APP_DIR to $BACKUP_DIR"
    restore
    exit 1
  fi
done

# Move things from update folder to application folder
for x in $UPDATE_APP_DIR/* $UPDATE_APP_DIR/.[!.]* $UPDATE_APP_DIR/..?*; do
  if [ -e "$x" ]; then mv -- "$x" $ORIGINAL_APP_DIR/; fi
  if [ $? -ne 0 ]; then
    echo "Unnable to move file $x from $UPDATE_APP_DIR to $ORIGINAL_APP_DIR"
    restore
    exit 1
  fi
done

# Remove backup folder
rm -rf "$BACKUP_DIR"

exit 0;