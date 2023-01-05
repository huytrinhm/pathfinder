#!/usr/bin/env python

import tkinter as tk
from tkinter import font, filedialog
import time

from configs import *
from manage_maps import save_map, load_map
from geometry import in_polygon, intersect, orientation, snap_point
from graph import generate_graph, pathfind, remove_start_end

map = []
graph = {}
start_coords = ()
end_coords = ()
path = []

is_editing_map = True

toggle_point = False


def main():
    window = tk.Tk()
    window.title("Pathfinding")
    window.resizable(False, False)

    global WINDOW_HEIGHT
    global WINDOW_WIDTH
    if WINDOW_HEIGHT == 0:
        WINDOW_HEIGHT = window.winfo_screenheight() * 3 / 4
    if WINDOW_WIDTH == 0:
        WINDOW_WIDTH = window.winfo_screenwidth() * 3 / 4

    window.geometry(
        "%dx%d+%d+%d"
        % (
            WINDOW_WIDTH,
            WINDOW_HEIGHT,
            window.winfo_screenwidth() / 2 - WINDOW_WIDTH / 2,
            window.winfo_screenheight() / 2 - WINDOW_HEIGHT / 2,
        )
    )

    font.nametofont("TkDefaultFont").configure(family=FONT_FAMILY, size=FONT_SIZE)

    root_frame = tk.Frame(window).pack(padx=PADDING, pady=PADDING)

    menu_frame = tk.Frame(root_frame)
    menu_frame.pack(side=tk.TOP, padx=PADDING, pady=PADDING, fill="x")

    map_menu = tk.Frame(menu_frame)
    map_menu.pack(side=tk.LEFT)

    tk.Button(map_menu, text="Save Map", command=on_save_map).pack(
        side=tk.LEFT, padx=PADDING
    )
    tk.Button(map_menu, text="Load Map", command=on_load_map).pack(
        side=tk.LEFT, padx=PADDING
    )
    tk.Button(map_menu, text="Edit Map", command=on_edit_map).pack(
        side=tk.LEFT, padx=PADDING
    )

    points_menu = tk.Frame(menu_frame)
    points_menu.pack(side=tk.RIGHT)

    global map_fill
    map_fill = tk.BooleanVar()
    map_fill.trace_add("write", lambda *_: update_canvas())
    tk.Checkbutton(points_menu, text="Map fill", variable=map_fill).pack(
        side=tk.LEFT, padx=PADDING
    )

    global show_graph
    show_graph = tk.BooleanVar()
    show_graph.trace_add("write", lambda *_: update_canvas())
    tk.Checkbutton(points_menu, text="Show graph", variable=show_graph).pack(
        side=tk.LEFT, padx=PADDING
    )

    global start_coords_label
    start_coords_label = tk.Label(points_menu, text="start = {...; ...}")
    start_coords_label.pack(side=tk.LEFT, padx=PADDING)

    global end_coords_label
    end_coords_label = tk.Label(points_menu, text="end = {...; ...}")
    end_coords_label.pack(side=tk.LEFT, padx=PADDING)

    global distance_label
    distance_label = tk.StringVar(value="Distance: ...")
    tk.Label(points_menu, textvariable=distance_label).pack(side=tk.LEFT, padx=PADDING)

    global canvas
    canvas = tk.Canvas(root_frame, bg="#ffffff")
    canvas.pack(padx=PADDING, pady=PADDING, expand=True, fill="both")

    global CANVAS_WIDTH
    global CANVAS_HEIGHT
    canvas.update()
    CANVAS_WIDTH = canvas.winfo_width()
    CANVAS_HEIGHT = canvas.winfo_height()

    status_frame = tk.Frame(root_frame)
    status_frame.pack(side=tk.BOTTOM, padx=PADDING, pady=PADDING, fill="x")

    global log
    log = tk.StringVar()
    tk.Label(status_frame, textvariable=log).pack(side=tk.LEFT, padx=PADDING)

    global cursor_coords_log
    cursor_coords_log = tk.StringVar()
    cursor_coords_log.set("(0; 0)")
    tk.Label(
        status_frame, textvariable=cursor_coords_log, font=font.Font(family="Consolas")
    ).pack(side=tk.RIGHT, padx=PADDING)

    canvas.bind("<Motion>", on_mouse_move)
    canvas.bind("<Button-1>", on_mouse_click)
    window.bind("<Shift_L>", on_shift)

    draw_grid()
    update_canvas()
    window.mainloop()


def on_save_map():
    if is_editing_map:
        return

    file = filedialog.asksaveasfilename(
        confirmoverwrite=True,
        defaultextension=".map",
        filetypes=[("Map files", "*.map")],
        title="Save Map",
    )
    if not file:
        return

    save_map(map, file, TILE_SIZE)
    log.set("Saved to " + file)


def on_load_map():
    global map, graph, is_editing_map
    reset()
    file = filedialog.askopenfilename(
        defaultextension=".map", filetypes=[("Map files", "*.map")], title="Load Map"
    )
    if not file:
        return

    map = load_map(file, TILE_SIZE)
    start_time = time.time()
    graph = generate_graph(map)
    duration = time.time() - start_time
    is_editing_map = False
    update_canvas()
    log.set(f"Loaded {file} in {duration:.10f}s. Use shift key to toggle between start/end point.")


def on_edit_map():
    global is_editing_map
    if is_editing_map:
        return

    reset()

    if map:
        map.pop()

    is_editing_map = True
    update_canvas()


def on_mouse_move(event):
    draw_cursor(event.x, event.y)
    cursor_coords_log.set(f"({event.x:d}; {event.y:d})")


def on_shift(event):
    global toggle_point
    toggle_point = not toggle_point


def on_mouse_click(event):
    global is_editing_map
    if is_editing_map:
        snapped_coords = snap_point(event.x, event.y, TILE_SIZE)
        if map:
            if snapped_coords in map and (len(map) == 1 or snapped_coords != map[0]):
                while map[-1] != snapped_coords:
                    map.pop()
                map.pop()
            else:
                is_intersect = False
                for k in range(len(map) - 2):
                    if snapped_coords == map[0] and k == 0:
                        continue
                    if intersect(map[-1], snapped_coords, map[k], map[k + 1]):
                        is_intersect = True
                        break

                if not is_intersect:
                    if len(map) > 2:

                        if orientation(map[-2], map[-1], snapped_coords) == 0:
                            map.pop()

                        if snapped_coords == map[0]:
                            if orientation(map[-1], map[0], map[1]) == 0:
                                map.pop(0)

                            map.append(map[0])
                            is_editing_map = False
                            global graph
                            start_time = time.time()
                            graph = generate_graph(map)
                            duration = time.time() - start_time
                            log.set(f"Generated graph in {duration:.10f}s. Use shift key to toggle between start/end point.")
                        else:
                            map.append(snapped_coords)
                    elif snapped_coords != map[0]:
                        map.append(snapped_coords)
                else:
                    log.set("Line is intersecting.")
        else:
            map.append(snapped_coords)
    elif in_polygon(map, event.x, event.y):
        global start_coords, end_coords
        reset(False)
        if not toggle_point:
            start_coords = event.x, event.y
            start_coords_label.config(text=f"start = {{{event.x}; {event.y}}}")
        else:
            end_coords = event.x, event.y
            end_coords_label.config(text=f"end = {{{event.x}; {event.y}}}")

        if start_coords and end_coords:
            global path
            start_time = time.time()
            path, dist = pathfind(graph, map, start_coords, end_coords)
            distance_label.set(f"Distance: {dist / TILE_SIZE:.2f}")
            duration = time.time() - start_time
            log.set(f"Path found in {duration:.10f}s. Use shift key to toggle between start/end point.")
    else:
        log.set("Invalid point. Use shift key to toggle between start/end point.")

    update_canvas()
    draw_cursor(event.x, event.y)


def reset(points=True):
    global start_coords, end_coords, path, graph
    if points:
        start_coords = ()
        end_coords = ()
    path = []

    graph = remove_start_end(graph)


def update_canvas():
    canvas.delete("cursor", "map", "path", "start", "end", "graph")

    if not is_editing_map and map and map_fill.get():
        canvas.create_polygon(map[:-1], fill=MAP_FILL_COLOR, tags="map")

    if not is_editing_map and show_graph.get():
        for u in graph:
            u_coords = ()
            if u == -1:
                u_coords = start_coords
            elif u == -2:
                u_coords = end_coords
            else:
                u_coords = map[u]

            for v in graph[u]:
                if v < u:
                    continue

                v_coords = ()
                if v == -1:
                    v_coords = start_coords
                elif v == -2:
                    v_coords = end_coords
                else:
                    v_coords = map[v]

                if u_coords and v_coords:
                    canvas.create_line(
                        u_coords, v_coords, fill=PREVIEW_COLOR, tags="graph"
                    )

    draw_lines(map, MAP_COLOR, LINE_WIDTH, tags="map")

    draw_lines(path, PATH_COLOR, LINE_WIDTH, tags="path")

    if start_coords:
        draw_dot(start_coords, START_POINT_COLOR, tags="start")
    if end_coords:
        draw_dot(end_coords, END_POINT_COLOR, tags="end")


def draw_grid():
    MAP_WIDTH = CANVAS_WIDTH // TILE_SIZE
    MAP_HEIGHT = CANVAS_HEIGHT // TILE_SIZE

    for i in range(MAP_WIDTH + 1):
        canvas.create_line(
            i * TILE_SIZE, 0, i * TILE_SIZE, CANVAS_HEIGHT, fill=GRID_COLOR, tags="grid"
        )

    for i in range(MAP_HEIGHT + 1):
        canvas.create_line(
            0, i * TILE_SIZE, CANVAS_WIDTH, i * TILE_SIZE, fill=GRID_COLOR, tags="grid"
        )


def draw_dot(coords, fill, tags=""):
    x, y = coords
    dot_start_x = x - DOT_RADIUS
    dot_start_y = y - DOT_RADIUS

    dot_end_x = x + DOT_RADIUS
    dot_end_y = y + DOT_RADIUS

    canvas.create_oval(
        dot_start_x, dot_start_y, dot_end_x, dot_end_y, fill=fill, outline="", tags=tags
    )


def draw_lines(vertices, fill, width, tags=""):
    prev = ()
    for u in vertices:
        draw_dot(u, fill, tags=tags)
        if prev:
            canvas.create_line(prev, u, fill=fill, width=width, tags=tags)

        prev = u


def draw_cursor(x, y):
    canvas.delete("cursor")
    if not is_editing_map:
        if not map:
            return

        if not toggle_point:
            dot_color = START_POINT_COLOR if in_polygon(map, x, y) else PREVIEW_COLOR
        else:
            dot_color = END_POINT_COLOR if in_polygon(map, x, y) else PREVIEW_COLOR
    else:
        snapped_coords = snap_point(x, y, TILE_SIZE)
        dot_color = CURSOR_COLOR
        if map:
            canvas.create_line(
                map[0],
                snapped_coords,
                fill=PREVIEW_COLOR,
                width=LINE_WIDTH,
                tags="cursor",
            )
            canvas.create_line(
                map[-1],
                snapped_coords,
                fill=PREVIEW_COLOR,
                width=LINE_WIDTH,
                tags="cursor",
            )

            if len(map) > 2 and snapped_coords == map[0]:
                draw_dot(snapped_coords, START_POINT_COLOR, tags="cursor")
            elif snapped_coords in map:
                draw_dot(snapped_coords, END_POINT_COLOR, tags="cursor")
            else:
                draw_dot(snapped_coords, PREVIEW_COLOR, tags="cursor")
        else:
            draw_dot(snapped_coords, PREVIEW_COLOR, tags="cursor")

    draw_dot((x, y), dot_color, tags="cursor")


if __name__ == "__main__":
    main()
