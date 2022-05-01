import tkinter as tk
import random
import copy

class Genesis():
    def __init__(self, users, currency):
        global network_currency
        network_currency = users * currency
        global created_genesis
        created_genesis = True

        label = ""
        for i in range(users):
            label += "-> (u" + str(i) + ", " + str(currency) + "), v" + str(i) + "\n"
        label += "-> (u" + str(users) + ", " + str(int(network_currency/2) - 1) + "), v" + str(users) + "\n"
        global bNode
        bNode = users
        label += "n0"
        size_tuple = determineSize(label)

        global root
        text = root.create_text(size_tuple[2] - size_tuple[0], size_tuple[3] - size_tuple[1], text=label)
        root.itemconfig(text, fill="#8763AD")
        guiItem = MakeGUI(text)

        global events
        events.append([self, 1])

        self.outputs = {users: int(network_currency/2) - 1}
        self.id = 0
        self.verified = True
        self.neighbors = []
        self.after = []
        self.guiObject = guiItem
        global node_dict
        node_dict[0] = self

        global validators
        delegated_stake = {users: int(network_currency/2) - 1}
        validators[users] = Validator()
        for i in range(users):
            self.outputs[i] = currency
            delegated_stake[i] = currency
            validators[i] = Validator()
        global node_dict_copies
        global delegated_stake_copies
        for i in range(users+1):
            node_dict_copies[i] = copy.deepcopy(node_dict)
            delegated_stake_copies[i] = copy.deepcopy(delegated_stake)
        network_currency += int(network_currency/2) - 1

    def calculateNet(self, world):
        dictionary = copy.deepcopy(self.outputs)
        for node_id in self.neighbors:
            node = world[node_id]
            spendings = node.inputs[self.id]
            for owner_key in spendings.keys():
                dictionary[owner_key] -= spendings[owner_key]

        return dictionary

    def isverified(input):
        return True

class Transaction():
    def __init__(self, input_objects=None, output_objects=None, validator_num=None, isglobal=True, inputs_l=None, outputs_l=None, validator_num_l=None, id_l=None, world=None):
        """
        output_objects, inputs_objects: list of tk.Entry
        """
        if isglobal:
            inputs = {}
            outputs = {}
            input_user_count = 0
            output_user_count = 0
            input_users_info = []
            output_users_info = []

            for object_tuple in input_objects:
                test_value = object_tuple[0].get()
                if test_value != "":
                    node = 0
                    user = 0
                    currency = 0
                    for i, input_object in enumerate(object_tuple):
                        if i == 0:
                            node = int(input_object.get())
                        elif i == 1:
                            user = int(input_object.get())
                        else:
                            currency = int(input_object.get())

                    if node in inputs:
                        node_dict1 = inputs[node]
                        if user in node_dict1:
                            node_dict1[user] += currency
                        else:
                            node_dict1[user] = currency
                    else:
                        inputs[node] = {user: currency}

                    input_user_count += 1
                    input_users_info.append((user, currency))

            for object_tuple in output_objects:
                test_value = object_tuple[0].get()
                if test_value != "":
                    user = 0
                    currency = 0
                    for i, output_object in enumerate(object_tuple):
                        if i == 0:
                            user = int(output_object.get())
                        else:
                            currency = int(output_object.get())

                    if user in outputs:
                        outputs[user] += currency
                    else:
                        outputs[user] = currency

                    output_user_count += 1
                    output_users_info.append((user, currency))

            label = ""
            for i in range(max(input_user_count, output_user_count)):
                if i < input_user_count and i < output_user_count:
                    label += "(u" + str(input_users_info[i][0]) + ", " + str(input_users_info[i][1]) + "), -> (u" + str(output_users_info[i][0]) + ", " + str(output_users_info[i][1]) + ")\n"
                elif i < input_user_count and i >= output_user_count:
                    label += "(u" + str(input_users_info[i][0]) + ", " + str(input_users_info[i][1]) + ")\n"
                else:
                    label += "-> (u" + str(output_users_info[i][0]) + ", " + str(output_users_info[i][1]) + ")\n"

            global node_id
            node_id += 1
            label = label + "n" + str(node_id) + ", v" + validator_num
            size_tuple = determineSize(label)

            global root
            text = root.create_text(size_tuple[2] - size_tuple[0], size_tuple[3] - size_tuple[1], text=label)
            guiItem = MakeGUI(text)

            global node_dict
            for i in inputs.keys():
                if i in node_dict:
                    guiItem.newArrowFromSelf(node_dict[i])
                    node_dict[i].neighbors.append(node_id)

            global events
            events.append((self, events[-1][1]))

            self.inputs = inputs
            self.outputs = outputs
            self.validator = int(validator_num)
            self.new_validator = False
            global delegated_stake_copies
            if not int(validator_num) in delegated_stake_copies:
                self.new_validator = True
                delegated_stake_copy = {}
                for i, dict in enumerate(delegated_stake_copies.values()):
                    dict[int(validator_num)] = 0
                    if i == 0: delegated_stake_copy = copy.deepcopy(dict)
                delegated_stake_copies[int(validator_num)] = delegated_stake_copy

                global node_dict_copies
                node_dict_copies[int(validator_num)] = copy.deepcopy(node_dict_copies[0])

                global validators
                validators[int(validator_num)] = Validator()

            self.verified = False
            self.acks = []
            self.verified_acks = []
            self.neighbors = []

            self.id = node_id
            node_dict[node_id] = self

            self.guiObject = guiItem
        else:
            self.inputs = inputs_l
            self.outputs = outputs_l
            self.validator = validator_num_l
            self.verified = False
            self.neighbors = []
            self.after = []

            self.id = id_l
            world[id_l] = self
            self.node_world = world

        self.value = 0
        for v in self.outputs.values():
            self.value += v

    @staticmethod
    def canInit(input_node, world):
        """
        Precondition that node.inputs all must exist in world
        """
        for k, v in input_node.inputs.items():
            node = world[k]
            if not node.verified: return False
            for owner_key in v.keys():
                if v[owner_key] < 0: return False
                if not owner_key in node.outputs: return False
            net = node.calculateNet(world)
            for owner_key in v.keys():
                if not owner_key in net: return False
                if net[owner_key] - v[owner_key] < 0 : return False
        return True

    def isverified(self, world):
        if self.verified: return True
        global node_dict
        for k in self.inputs.keys():
            if not self.node_world[k].verified: return False
        stake = 0
        for ack in node_dict[self.id].acks:
            stake += world[ack.validator]
        global network_currency
        if stake > network_currency * 2/3: return True
        return False

    def calculateNet(self, world):
        dictionary = copy.deepcopy(self.outputs)
        for node_id in self.neighbors:
            node = world[node_id]
            spendings = node.inputs[self.id]
            for owner_key in spendings.keys():
                try:
                    dictionary[owner_key] -= spendings[owner_key]
                except KeyError:
                    pass

        return dictionary

    def erase(self):
        global root
        global node_dict
        for lst1 in self.guiObject.edges:
            for lst2 in lst1[0].edges:
                if lst2[1] == lst1[1]:
                    root.delete(lst2[1])
                    lst1[0].edges.remove(lst2)
                    break
        for lst1 in self.guiObject.edges:
            self.guiObject.edges.remove(lst1)
        root.delete(self.guiObject.widget)
        del self.guiObject

        node_dict.pop(self.id)
        if self.new_validator:
            global validators
            validators.pop(self.validator)

            global node_dict_copies
            node_dict_copies.pop(self.validator)

            global delegated_stake_copies
            delegated_stake_copies.pop(self.validator)
            for dict in delegated_stake_copies.values():
                dict.pop(self.validator)

class Validator():
    def __init__(self):
        self.acks = []

class Ack():
    def __init__(self, validator, reference):
        global node_dict
        node = node_dict[reference]
        existing_acks = [a.validator for a in node.acks]
        if not validator in existing_acks:
            node.acks.append(self)
            label = "v" + str(validator)
            size_tuple = determineSize(label)

            global root
            text = root.create_text(size_tuple[2] - size_tuple[0], size_tuple[3] - size_tuple[1], text=label)

            guiItem = MakeGUI(text)
            global validators
            if len(validators[validator].acks) != 0:
                guiItem.newArrowFromSelf(validators[validator].acks[-1])
            guiItem.newArrowFromSelf(node_dict[reference])

            self.validator = validator
            self.reference = reference
            self.guiObject = guiItem
            validators[validator].acks.append(self)
        else:
            return None

    def erase(self):
        global root
        global node_dict
        global validators
        for lst1 in self.guiObject.edges:
            for lst2 in lst1[0].edges:
                if lst2[1] == lst1[1]:
                    root.delete(lst2[1])
                    lst1[0].edges.remove(lst2)
                    break
        for lst1 in self.guiObject.edges:
            self.guiObject.edges.remove(lst1)
        root.delete(self.guiObject.widget)
        del self.guiObject
        root.itemconfig(node_dict[self.reference].guiObject.widget, fill="#000000")

        node_dict[self.reference].verified = False
        node_dict[self.reference].acks.remove(self)
        global node_dict_copies
        for world in node_dict_copies.values():
            if self.reference in world:
                for id in world[self.reference].inputs.keys():
                    try:
                        world[id].neighbors.remove(self.reference)
                    except:
                        pass
                world.pop(self.reference)
        validators[self.validator].acks.remove(self)

def updateGUI():
    if not created_genesis:
        setGensis()
    handleInput()
    global window
    window.after(2000, updateGUI)

def setGensis():
    while True:
        users = input("Number of users in network: ")
        if not users.isnumeric() or (int(users) < 2 or int(users) > 10):
            print("please input number in range 2..10")
            continue
        else:
            users = int(users)
            break

    while True:
        currency = input("Amount of currency for each user: ")
        if not currency.isnumeric() or int(currency) <= 0:
            print("please input a positive number")
            continue
        else:
            currency = int(currency)
            break

    while True:
        byzantine_mode_input = input("Demo with byzantine behavios [Y/N]?: ")
        if not byzantine_mode_input in ['Y', 'N']:
            print("invalid input")
            continue
        else:
            global byzantine_mode
            if byzantine_mode_input == 'Y':
                byzantine_mode = True
            else:
                byzantine_mode = False
            break

    a = Genesis(users, currency)

def handleInput():
    while True:
        user_input = input("\ninput 't' for new transaction \ninput 'n' to update network state \ninput 'u' to undo step \ninput 'e' to end application \ninput: ")
        if not user_input in ('t', 'n', 'u', 'e'):
            print("\ninvalid input")
            continue
        else:
            if user_input == 't':
                handleTransaction()
            elif user_input == 'n':
                handleUpdate()
            elif user_input == 'u':
                handleUndo()
            elif user_input == 'e':
                global window
                window.destroy()
            break

def handleTransaction():
    def handleTransactionOK():
        input_currency = 0
        output_currency = 0
        display_error = False
        filled = True
        badNode = False

        global node_dict
        for object_tuple in input_objects:
            fills = []
            fillcheck = 0
            for input_object in object_tuple:
                value = input_object.get()
                fills.append(value)
                if value != "":
                    fillcheck += 1
                if value != "" and (not value.isnumeric() or int(value) < 0):
                    display_error = True
            try:
                input_currency += int(object_tuple[-1].get())
            except:
                pass

            if fillcheck not in (0,3):
                filled = False

            if len(fills) == 3 and fills[0].isnumeric() and not int(fills[0]) in node_dict:
                badNode = True

        for object_tuple in output_objects:
            fillcheck = 0
            for output_object in object_tuple:
                value = output_object.get()
                if value != "":
                    fillcheck += 1
                if value != "" and (not value.isnumeric() or int(value) < 0):
                    display_error = True
            try:
                output_currency += int(object_tuple[-1].get())
            except:
                pass

            if fillcheck not in (0,2):
                filled = False

        global bNode
        global byzantine_mode
        validator_value = validator_entry.get()
        if not filled or validator_value == "":
            error_entry.delete(0, tk.END)
            error_entry.insert(0, "an input or output is incomplete")
        elif display_error or (not validator_value.isnumeric() or int(validator_value) < 0):
            error_entry.delete(0, tk.END)
            error_entry.insert(0, "all inputs should be integers >= 0")
        elif input_currency != output_currency:
            error_entry.delete(0, tk.END)
            error_entry.insert(0, "input currency of " + str(input_currency) + " not equal to output currency of " + str(output_currency))
        elif badNode:
            error_entry.delete(0, tk.END)
            error_entry.insert(0, "only reference node for input on the GUI")
        elif int(validator_value) == bNode and byzantine_mode:
            error_entry.delete(0, tk.END)
            error_entry.insert(0, "validator is byzantine and will cause byzantine stake to exceed 1/3 of network's")
        else:
            a = Transaction(input_objects=input_objects, output_objects=output_objects, validator_num=validator_value, isglobal=True)
            win.destroy()

    def handleTransactionCancel():
        win.destroy()

    print("\ninput transaction inputs and outputs on GUI")
    win = tk.Toplevel()
    for i in range(5):
        win.columnconfigure(i, weight=1)
    for i in range(15):
        win.rowconfigure(i, weight=1)
    input_label = tk.Label(win, text="inputs")
    input_label.grid(row=0, column=0, columnspan=3)
    output_label = tk.Label(win, text="outputs")
    output_label.grid(row=0, column=3, columnspan=2)

    input_node_label = tk.Label(win, text="node")
    input_node_label.grid(row=1, column=0)
    input_user_label = tk.Label(win, text="user")
    input_user_label.grid(row=1, column=1)
    input_currency_label = tk.Label(win, text="currency")
    input_currency_label.grid(row=1, column=2)

    output_user_label = tk.Label(win, text="user")
    output_user_label.grid(row=1, column=3)
    output_currency_label = tk.Label(win, text="currency")
    output_currency_label.grid(row=1, column=4)

    input_objects = []
    output_objects = []
    for i in range(2, 12):
        input_node_entry = tk.Entry(win)
        input_node_entry.grid(row=i, column=0)
        input_user_entry = tk.Entry(win)
        input_user_entry.grid(row=i, column=1)
        input_currency_entry = tk.Entry(win)
        input_currency_entry.grid(row=i, column=2)
        input_objects.append((input_node_entry, input_user_entry, input_currency_entry))

        output_user_entry = tk.Entry(win)
        output_user_entry.grid(row=i, column=3)
        output_currency_entry = tk.Entry(win)
        output_currency_entry.grid(row=i, column=4)
        output_objects.append((output_user_entry, output_currency_entry))

    validator_label = tk.Label(win, text="validator: ")
    validator_label.grid(row=12, column=0)
    validator_entry = tk.Entry(win)
    validator_entry.grid(row=12, column=1, columnspan=4, sticky='nesw')
    ok_button = tk.Button(win, text="ok", command=handleTransactionOK)
    ok_button.grid(row=13, column=0)
    cancel_button = tk.Button(win, text="cancel", command=handleTransactionCancel)
    cancel_button.grid(row=13, column=1)
    error_entry = tk.Entry(win)
    error_entry.grid(row=14, column=0, columnspan=5, sticky='nesw')

def handleUpdate():
    def handleUpdateHelper(user_input):
        global byzantine_mode
        global delegated_stake_copies
        original_stake = copy.deepcopy(delegated_stake_copies)
        ack_lst = []
        if user_input == 'z':
            user_input = random.choice(['x', 'y'])
        global events
        new_transactions = events[events[-1][1]:]
        iterations = 0
        new_acks = 0
        for k, world in node_dict_copies.items():
            random.shuffle(new_transactions)
            processed = 0
            while processed != len(new_transactions):
                for tup in new_transactions:
                    if tup[0].id in world:
                        pass
                    else:
                        inputs_exist = True
                        for id in tup[0].inputs.keys():
                            if not id in world:
                                inputs_exist = False

                        if inputs_exist:
                            processed += 1
                            copied_trans = Transaction(inputs_l=tup[0].inputs, outputs_l=tup[0].outputs, validator_num_l=tup[0].validator, id_l=tup[0].id, world=world, isglobal=False)
                            for i in copied_trans.inputs.keys():
                                world[i].after.append(copied_trans.id)
                            world[tup[0].id] = copied_trans
                            global bNode
                            if k == bNode and user_input == 'y' and byzantine_mode:
                                pass
                            elif (k == bNode and user_input == 'x' and byzantine_mode) or Transaction.canInit(copied_trans, world):
                                ack = Ack(k, copied_trans.id)
                                ack_lst.append(ack)
                                new_acks += 1
                                for i in copied_trans.inputs.keys():
                                    world[i].neighbors.append(copied_trans.id)

        old_acks = 0
        while old_acks != new_acks:
            old_acks = new_acks
            for k, world in node_dict_copies.items():
                for tup in new_transactions:
                    if tup[0].id in world:
                        trans = world[tup[0].id]
                        newly_verified = trans.isverified(delegated_stake_copies[k])
                        if newly_verified != trans.verified:
                            global node_dict
                            global root
                            world_node = node_dict[trans.id]
                            root.itemconfig(world_node.guiObject.widget, fill="#8763AD")
                            global validators
                            world_node.verified = True

                            delegated_stake_copies[k][trans.validator] += trans.value
                            for id, outputs in trans.inputs.items():
                                value = 0
                                for v in outputs.values():
                                    value += v
                                try:
                                    delegated_stake_copies[k][world[id].validator] -= value
                                except:
                                    for id2, v2 in outputs.items():
                                        delegated_stake_copies[k][id2] -= v2
                            trans.verified = True

                            for contingent_id in trans.after:
                                contingent_trans = world[contingent_id]
                                if Transaction.canInit(contingent_trans, world) and not (k == bNode and user_input == 'y' and byzantine_mode):
                                    ack = Ack(k, contingent_id)
                                    if not ack is None:
                                        for i in contingent_trans.inputs.keys():
                                            world[i].neighbors.append(contingent_trans.id)
                                        new_acks += 1
                                        ack_lst.append(ack)

        events.append([ack_lst, original_stake, len(events)+1])

    global byzantine_mode
    while True and byzantine_mode:
        user_input = input("\nchoose byzantine validator behaviors: \ninput 'x' to ack everything \ninput 'y' to ack nothing \ninput 'z' for random \ninput 'b' to go back \ninput 'e' to end application \ninput: ")
        if not user_input in ('x', 'y', 'z', 'b', 'e'):
            print("\ninvalid input")
            continue
        else:
            if user_input in ('x', 'y', 'z'):
                handleUpdateHelper(user_input)
            elif user_input == 'b':
                pass
            elif user_input == 'e':
                global window
                window.destroy()
            break

    while True and not byzantine_mode:
        handleUpdateHelper('x')
        break

def handleUndo():
    global events
    tup = events[-1]
    if isinstance(tup[0], list):
        for ack in tup[0]:
            ack.erase()
        del events[-1]
        global delegated_stake_copies
        delegated_stake_copies = tup[1]
    elif isinstance(tup[0], Transaction):
        tup[0].erase()
        del events[-1]

def determineSize(text):
    #credits: https://stackoverflow.com/questions/18800860/dynamic-sizing-tkinter-canvas-text
    scratch = tk.Canvas()
    id = scratch.create_text((0, 0), text=text)
    return scratch.bbox(id)

class MakeGUI():
    #credits: https://stackoverflow.com/questions/65033543/how-to-move-text-inside-canvas-in-tkinter
    def __init__(self, widget):
        root.tag_bind(widget, "<Button-1>", self.drag_start)
        root.tag_bind(widget, "<B1-Motion>", self.mov)
        self.widget = widget
        self.edges = []

    def newArrowFromSelf(self, other_obj):
        self_coords = root.coords(self.widget)
        other_coords = root.coords(other_obj.guiObject.widget)
        line = root.create_line(self_coords[0], self_coords[1], other_coords[0], other_coords[1], arrow=tk.LAST)
        other_obj.guiObject.edges.append([self, line, "tail"])
        self.edges.append([other_obj.guiObject, line, "head"])

    def drag_start(self, event):
        widget = event.widget
        widget.startX, widget.startY = event.x, event.y

    def mov(self, event):
        widget = event.widget
        widget.move(self.widget, event.x-widget.startX, event.y-widget.startY)
        widget.startX, widget.startY = event.x, event.y
        global root
        for lst in self.edges:
            guiObject = lst[0]
            line = lst[1]
            marking = lst[2]

            other_coords = root.coords(guiObject.widget)
            other_dim = root.bbox(guiObject.widget)
            self_coords = root.coords(self.widget)
            self_dim = root.bbox(self.widget)
            otherrad = (((other_dim[2] - other_dim[0])/2)**2 + ((other_dim[3] - other_dim[1])/2)**2)**0.5
            selfrad = (((self_dim[2] - self_dim[0])/2)**2 + ((self_dim[3] - self_dim[1])/2)**2)**0.5
            other_intersects = circle_line_segment_intersection((other_coords[0], other_coords[1]), otherrad, (other_coords[0], other_coords[1]), (self_coords[0], self_coords[1]))
            self_intersects = circle_line_segment_intersection((self_coords[0], self_coords[1]), selfrad, (other_coords[0], other_coords[1]), (self_coords[0], self_coords[1]))
            smallest_pair = []
            for pt1 in other_intersects:
                for pt2 in self_intersects:
                    dist = (pt2[1] - pt1[1])**2 + (pt2[0] - pt1[0])**2
                    if len(smallest_pair) == 0:
                        smallest_pair = [pt1, pt2, dist]
                    else:
                        if dist < smallest_pair[-1]:
                            smallest_pair = [pt1, pt2, dist]
            if marking == "head":
                new_line = root.create_line(smallest_pair[1][0], smallest_pair[1][1], smallest_pair[0][0], smallest_pair[0][1], arrow=tk.LAST)
            else:
                new_line = root.create_line(smallest_pair[0][0], smallest_pair[0][1], smallest_pair[1][0], smallest_pair[1][1], arrow=tk.LAST)
            lst[1] = new_line
            for lst1 in guiObject.edges:
                if lst1[1] == line:
                    lst1[1] = new_line
                    break
            root.delete(line)

def circle_line_segment_intersection(circle_center, circle_radius, pt1, pt2, full_line=True, tangent_tol=1e-9):
    #credits: https://stackoverflow.com/questions/30844482/what-is-most-efficient-way-to-find-the-intersection-of-a-line-and-a-circle-in-py
    (p1x, p1y), (p2x, p2y), (cx, cy) = pt1, pt2, circle_center
    (x1, y1), (x2, y2) = (p1x - cx, p1y - cy), (p2x - cx, p2y - cy)
    dx, dy = (x2 - x1), (y2 - y1)
    dr = (dx ** 2 + dy ** 2)**.5
    big_d = x1 * y2 - x2 * y1
    discriminant = circle_radius ** 2 * dr ** 2 - big_d ** 2

    if discriminant < 0:  # No intersection between circle and line
        return []
    else:  # There may be 0, 1, or 2 intersections with the segment
        intersections = [
            (cx + (big_d * dy + sign * (-1 if dy < 0 else 1) * dx * discriminant**.5) / dr ** 2,
             cy + (-big_d * dx + sign * abs(dy) * discriminant**.5) / dr ** 2)
            for sign in ((1, -1) if dy < 0 else (-1, 1))]  # This makes sure the order along the segment is correct
        if not full_line:  # If only considering the segment, filter out intersections that do not fall within the segment
            fraction_along_segment = [(xi - p1x) / dx if abs(dx) > abs(dy) else (yi - p1y) / dy for xi, yi in intersections]
            intersections = [pt for pt, frac in zip(intersections, fraction_along_segment) if 0 <= frac <= 1]
        if len(intersections) == 2 and abs(discriminant) <= tangent_tol:  # If line is tangent to circle, return just one point (as both intersections have same location)
            return [intersections[0]]
        else:
            return intersections

node_id = 0
node_dict = {} #overview of all nodes
bNode = None
node_dict_copies = {} #number of validator: dictionary of all nodes validator believes exist
delegated_stake_copies = {} #number of validator: delegated stake dictionary
validators = {} #number: Validator object

byzantine_mode = True
events = []
edges = {}
ack_count = 0
created_genesis = False
DIMENSIONS = "1200x600"
XDIMENSION = 1200
YDIMESION = 600

window = tk.Tk()
window.geometry(DIMENSIONS)
root = tk.Canvas(window, width=XDIMENSION, height=YDIMESION)
root.pack(fill = "both", expand=True)

window.after(2000, updateGUI)
window.mainloop()
