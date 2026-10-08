#!/bin/bash
# 現在のウィンドウのグループを引き継いで新ウィンドウを作成
TABBY=~/.tmux/plugins/tabby/bin/tabby
CLIENT_TTY=$(tmux display-message -p '#{client_tty}' 2>/dev/null)
GROUP=$(tmux show-window-option -v @tabby_group 2>/dev/null)

if [ -n "$GROUP" ]; then
    "$TABBY" new-window -client-tty "$CLIENT_TTY" -group "$GROUP"
else
    "$TABBY" new-window -client-tty "$CLIENT_TTY"
fi
