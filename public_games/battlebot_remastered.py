import asyncio
import random
import time
import database
import json
import csv

db = database.Database()
import disnake.ext.commands

action_to_process = False

def getCandies(user: disnake.Member):
    db.get_tickets(user)


def addCandies(user, n_candy):
    db.award_tickets(n_candy, user, "Battle")

enemy_list = {}

def getEnemy():
    """
    Returns:
        (monster_key, info_dict)
    info_dict contains keys: 'name', 'description', 'emote', 'rarity'
    """
    import csv
    import random
    path = './resources/monsters.csv'

    rarity_roll = random.randint(1, 100)
    if rarity_roll <= 50:
        rarity_target = "1"
    elif rarity_roll <= 75:
        rarity_target = "2"
    elif rarity_roll <= 85:
        rarity_target = "3"
    elif rarity_roll <= 94:
        rarity_target = "4"
    else:
        rarity_target = "5"

    candidates = []
    with open(path, encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            r = row.get('RARITY', '').strip()
            if r == rarity_target:
                candidates.append({
                    'name': row.get('NAME', '').strip(),
                    'description': row.get('DESCRIPTION', '').strip(),
                    'emote': row.get('EMOTE', '').strip(),
                    'rarity': r
                })

    # fallback: if no candidates for rarity, choose from whole file
    if not candidates:
        with open(path, encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                candidates.append({
                    'name': row.get('NAME', '').strip(),
                    'description': row.get('DESCRIPTION', '').strip(),
                    'emote': row.get('EMOTE', '').strip(),
                    'rarity': row.get('RARITY', '').strip()
                })

    chosen = random.choice(candidates)
    key = chosen['name']
    # Optionally, populate your global enemy_list mapping if you want:
    enemy_list[key] = chosen
    return key, chosen

def getFlavour(monster):
    flavour_list = [
        f'{monster} attacks!',
        f'{monster} wanders by!',
        f'{monster} crossed your path!',
        f'{monster} stakes their claim!',
        f'{monster} fights back!',
        f'{monster} has decided your fate!',
        f'{monster} takes a stab!',
        f'{monster} remembers where they are!',
        f'{monster} took a wrong turn!',
        f'{monster} committed piracy!',
        f'{monster} pinged everyone!',
        f'{monster} repeated 4 times!',
        f'{monster} draws near!',
        f'You are confronted by {monster} and its cohorts.',
        f'{monster} hasn\'t paid their taxes!',
        f'{monster} emerges from the earth!',
        f'{monster} wakes up from a nightmare!',
        f'{monster} forgets what day it is!',
        f'{monster} thinks this is a prank..?',
        f'{monster} jumpscares you!',
        f'{monster} readjusts their ~~Halloween~~ July mask.',
        f'{monster} befriends your mom!',
        f'{monster} wavedashes towards you!',
        f'{monster} shuffles towards you!',
        f'{monster} comes out to play!',
        f'{monster} confronts you!',
        f'{monster} draws near!',
        f'Oops! All {monster}!',
        f'Wild {monster} appeared!',
        f'You were accosted by {monster}!',
        f'{monster} has come to make an announcement.',
        f'{monster} has some POINTs!',
        f'{monster}, on the scene!',
        f'There\'s a {monster} among us!',
        f'{monster} broke TOS!',
        f'{monster} explodes gently.',
        f'{monster} exists in your general direction.',
        f'{monster} RPs in your general chat!',
        f'{monster} drinks all your iced coffee!',
        f'{monster} floats and gloats!',
        f'{monster} trips and faceplants!',
        f'{monster} thinks you\'re just playing!',
        f'{monster} chose trick!',
        f'{monster} hurls garbage at you!',
        f'{monster} comes back again!',
        f'{monster} is out of ideas!'
    ]

    valid = False

    while not valid:
        temp = random.choice(flavour_list)
        if len(temp) < 256:
            valid = True
    return temp


async def newEmbed(flavour, monster, time, health, maxhealth, actions='ATTACKS...', color=0xff0000):
    global hitpoints, old_deadlist, deadlist, enemy_list

    monster_info = enemy_list[monster]
    description = monster_info["description"]

    if min(500, 0.1 * maxhealth) > health > 1:
        health = 'LOW HP'

    alive_fighters = []
    dead_fighters = []
    t_dead_text = ''
    t_alive_text = ''
    alive_text = "Nobody is fighting!"
    dead_text = "Nobody is broke!"
    player_dead = False
    player_alive = False
    if len(hitpoints) < 1:
        alive_text = "Nobody has entered this battle!"
        dead_text = "Nobody is broke!"
    else:
        for i in hitpoints:
            temp_hp = hitpoints[i]
            if temp_hp <= 0:
                player_dead = True
                if i not in deadlist:
                    deadlist.append(i)
                if len(t_dead_text) >= 900:
                    t_dead_text = f'{t_dead_text}(+ more...)'
                    break
                the_user = await bot.get_or_fetch_user(i)
                t_dead_text = f'{t_dead_text}{the_user.name} (0/100 HP)\n'
            else:
                player_alive = True
                if len(t_alive_text) >= 900:
                    t_alive_text = f'{t_alive_text}(+ more...)'
                    break
                user = await bot.get_or_fetch_user(i)
                if i in userList:
                    t_alive_text = f'{t_alive_text}🛑 | {user.name} ({temp_hp}/100 HP)\n'
                else:
                    t_alive_text = f'{t_alive_text}🟢 | {user.name} ({temp_hp}/100 HP)\n'

    if player_dead:
        dead_text = t_dead_text
    if player_alive:
        alive_text = t_alive_text

    embed = disnake.Embed(title=f"{flavour}",
                          description=f"{monster_info['emote']}", color=color)
    embed.add_field(name="Monster Information", value=description, inline=False)
    embed.add_field(name="MONSTER HP", value=f"{health} / {maxhealth}", inline=True)
    if actions: embed.add_field(name=actions, value=time, inline=True)
    embed.add_field(name="EMPLOYEES:", value="_ _", inline=False)
    embed.add_field(name="THE FIGHTERS", value=alive_text, inline=True)
    embed.add_field(name="THE BROKE", value=dead_text, inline=True)

    return embed


difficulty = 0
old_userList = []
old_deadlist = []
deadlist = []
battleOngoing = False
monster_HP = 0
hitpoints = {}
dmgDone = {}
lastAttacker = 0
userList = []
turn = False
loss = False
fight_average = [0]
player_mercy = []
mercy_blacklist = []
spare_min = 1 # This will be set to 50% of the participants of the previous battle.

async def attackHandler(interaction):
    global monster_HP, hitpoints, lastAttacker
    if monster_HP > 0:

        m_dam, p_hp = await attack(interaction, hitpoints[interaction.author.id])

        # removes mercy
        if interaction.author.id in player_mercy:
            player_mercy.remove(interaction.author.id)
            mercy_blacklist.append(interaction.author.id)

        hitpoints[interaction.author.id] = p_hp
        monster_HP = monster_HP - m_dam

    else:
        sadEmbed = disnake.Embed(title='Too Late!',
                                 description='The monster has already been killed so you cannot attack it!')
        await interaction.send(embed=sadEmbed, ephemeral=True)

async def mercyHandler(interaction):
    # the player has chosen to give mercy
    global player_mercy, spare_min

    if interaction.author.id in player_mercy:
        #await interaction.send("You have already shown mercy!", ephemeral=True)
        sadEmbed = disnake.Embed(title="You've already shown mercy!",
                                 description='You are already giving the monster mercy, and cannot give it again!')
        await interaction.send(embed=sadEmbed, ephemeral=True)
        return
    if interaction.author.id in mercy_blacklist:
        sadEmbed = disnake.Embed(title='Betrayed!',
                                 description='You have betrayed the monster and cannot give mercy anymore!')
        await interaction.send(embed=sadEmbed, ephemeral=True)
        return

    # the player has not shown mercy yet
    player_mercy.append(interaction.author.id)

    if int((len(player_mercy) / spare_min) * 100) >= 100:
        add_str = "\nIf they survive until the end of the turn, they will be spared!"
    else:
        add_str = ""

    happyEmbed = disnake.Embed(title='Show some MERCY, human!', description=f"You choose to show mercy to the monster.\nThey are currently { int((len(player_mercy) / spare_min) * 100) }% spared{add_str}", color = disnake.Colour.yellow())
    happyEmbed.set_footer(text="If you betray your mercy, they won't trust you again!")
    await interaction.send(embed=happyEmbed, ephemeral=True)
    return

async def candyHandler(interaction):
    global hitpoints
    cur_can = getCandies(interaction.author)
    candyToLose = 0

    if cur_can < candyToLose:
        candyToLose = cur_can

    reward = 0
    dead_players = []
    injured_players = []

    for i in hitpoints:
        if hitpoints[i] == 0:
            dead_players.append(i)
        if hitpoints[i] < 100:
            injured_players.append(i)

    injured_players.sort()

    if len(dead_players) == 0 and len(injured_players) == 0:
        cEmbed = disnake.Embed(title=f'You try to pick up the fallen..',
                                description=f'Fortunately, there was nobody to revive!',
                                color=0x388500)
        userList.remove(interaction.author.id)
    elif len(dead_players) > 0:
        player = random.choice(dead_players)
        guild = interaction.guild
        user = guild.get_member(player)
        cEmbed = disnake.Embed(title=f'You spend a turn reviving {user.name}.',
                               description=f'{user.name} (<@{player}>) was healed by 20 health!',
                               color=0x65EA00)
        hitpoints[player] = 20
        deadlist.remove(player)
        if player not in userList:
            userList.append(player)
    else: # Nobody is dead and we know at least one person is injured, so let's heal them
        player = injured_players[0]
        guild = interaction.guild
        user = guild.get_member(player)
        cEmbed = disnake.Embed(title=f'You spend a turn healing {user.name}.',
                               description=f'{user.name} (<@{player}>) was healed by 35 health!',
                               color=0x65EA00)
        hitpoints[player] = hitpoints[player] + 35

    await interaction.send(embed=cEmbed, ephemeral=True)


async def healHandler(interaction):
    return await heal(interaction, hitpoints[interaction.author.id])


async def play_game(channel, bot2, optional_argument=None):
    global old_userList, deadlist, old_deadlist, battleOngoing, hitpoints, monster_HP, lastAttacker, userList, turn, loss, dmgDone, fight_average, action_to_process, bot, player_mercy, mercy_blacklist, spare_min
    bot=bot2

    if battleOngoing:
        return

    old_deadlist = deadlist
    deadlist = []

    hitpoints = {}
    dmgDone = {}
    monster, info = getEnemy()
    mname = info['name']
    flavour = getFlavour(mname)

    # mercy handling
    spare_min = int(len(old_userList) / 2)
    if spare_min < 5:
        spare_min = 5
    spare_min = 1

    player_mercy = []
    mercy_blacklist = []

    monster_HP_MAX = round(((len(old_userList)) * 400))


    if loss:
        monster_HP_MAX = int(monster_HP_MAX * 0.90)
    if monster_HP_MAX < 3400:
        monster_HP_MAX = 3400

    if len(fight_average) > 0:
        avg = sum(fight_average) / len(fight_average)
        print(f"Current Player Winrate: {avg}")
        if avg < 0.7:
            monster_HP_MAX = int(monster_HP_MAX - ((0.5 * monster_HP_MAX) * (1 - (avg / 2))))
        else:
            monster_HP_MAX = int(monster_HP_MAX * (1 + (avg - 0.7)))
        if len(fight_average) > 6:
            fight_average.pop(0)

    monster_HP_MAX = int(monster_HP_MAX * random.uniform(0.85, 1.35))

    if mname == 'Sans':
        monster_HP_MAX = 1

    if channel.id == 774573426689048586:
        #monster_HP_MAX = 1000
        pass

    monster_HP = monster_HP_MAX
    turnTime = 60
    battleTime = int(time.time())
    embed = await newEmbed(flavour, monster, f'...<t:{battleTime + 62}:R>', monster_HP, monster_HP_MAX)

    battleOngoing = True
    turn = True
    print(battleTime)
    turnCount = 0
    lastAttacker = None

    message = await channel.send(embed=embed, components=[
        disnake.ui.ActionRow(
            disnake.ui.Button(label="🗡️ Attack", custom_id=f"attack_enemy", style=disnake.Color(4),
                              disabled=False),
            disnake.ui.Button(label="💊 Heal", custom_id=f"heal_player", style=disnake.Color(1),
                              disabled=False),
            disnake.ui.Button(label="🕊️ Mercy", custom_id=f"mercy", style=disnake.Color(3),
                              disabled=False)
        )])

    @bot.listen("on_button_click")
    async def on_battle_press(interaction):
        global userList, hitpoints, action_to_process

        if interaction.component.custom_id != 'attack_enemy' and interaction.component.custom_id != 'heal_player' and interaction.component.custom_id != 'mercy':
            return

        if turn is False and battleOngoing is True:
            await interaction.send(content="The monster is currently taking their turn so you cannot act!",
                                   ephemeral=True)
            return

        if not battleOngoing:
            await interaction.response.send_message("There's not an ongoing battle!", ephemeral=True)
            userList = []
            return

        if interaction.author.id not in hitpoints:
            if interaction.author.id in old_deadlist:
                hitpoints[interaction.author.id] = 50
            else:
                hitpoints[interaction.author.id] = 100

        if hitpoints[interaction.author.id] <= 0:
            await interaction.response.send_message(
                content="GAME OVER!\nYou were defeated and have been disengaged from the battle!", ephemeral=True)
            return
        if interaction.author.id in userList:
            await interaction.response.send_message(content="You have already acted this turn!", ephemeral=True)
            return
        else:
            userList.append(interaction.author.id)

        if interaction.component.custom_id == 'attack_enemy' and battleOngoing is True:
            await attackHandler(interaction)
        elif interaction.component.custom_id == 'heal_player' and battleOngoing is True:
            if hitpoints[interaction.author.id] < 100:
                hitpoints[interaction.author.id] = await healHandler(interaction)
            else:
                await candyHandler(interaction)
        elif interaction.component.custom_id == 'mercy' and battleOngoing is True:
            await mercyHandler(interaction)
        else:
            await interaction.response.send_message("There's not an ongoing battle!", ephemeral=True)
            userList = []

        action_to_process = True

    while battleOngoing:
        userList = []
        if monster_HP <= 0 or len(player_mercy) >= spare_min:
            turn = False
            battleOngoing = False
            victory = True
        elif turnCount >= 10:
            turn = False
            battleOngoing = False
            victory = False
        while turn:
            await asyncio.sleep(1)
            if monster_HP <= 0:
                break
            if action_to_process:
                try:
                    await message.edit(
                        embed=await newEmbed(flavour, monster, f'<t:{battleTime + 62}:R>', monster_HP,
                                       monster_HP_MAX), components=[
                            disnake.ui.ActionRow(disnake.ui.Button(label="🗡️ Attack", custom_id=f"attack_enemy",
                                                                   style=disnake.Color(4), disabled=False),
                                                 disnake.ui.Button(label="💊 Heal", custom_id=f"heal_player",
                                                                   style=disnake.Color(1), disabled=False),
                                                 disnake.ui.Button(label="🕊️ Mercy", custom_id=f"mercy",
                                                                   style=disnake.Color(3),
                                                                   disabled=False))])
                except Exception as e:
                    print("Threw Exception! ", e)
                action_to_process = False
            if battleTime + turnTime < int(time.time()):
                userList = []
                battleTime = int(time.time())
                turnCount += 1
                turn = False

        if monster_HP > 0 and turnCount < 10:
            await message.edit(components=[
                disnake.ui.ActionRow(
                    disnake.ui.Button(label="🗡️ Attack", custom_id=f"attack_enemy", style=disnake.Color(4),
                                      disabled=True),
                    disnake.ui.Button(label="💊 Heal", custom_id=f"heal_player", style=disnake.Color(1),
                                      disabled=True),
                    disnake.ui.Button(label="🕊️ Mercy", custom_id=f"mercy", style=disnake.Color(3),
                                      disabled=True))])
            attacking = True
            attacked = {}
            attackstring = ''

            validTargets = []
            targetList = []

            for i in hitpoints:
                if hitpoints[i] > 0:
                    validTargets.append(i)

            atkcount = round((len(validTargets)) / 4)
            if atkcount > 15:
                atkcount = 15
            elif atkcount == 0:
                attacking = False
        else:
            attacking = False
        atk_time = int(time.time())
        if attacking:
            attackstring = ''
            while atkcount > 0 and attacking:
                if len(validTargets) == 0:
                    embed = await newEmbed(f"{mname} is taking their turn!", monster,
                                     f"...<t:{int(atk_time + 7 + atkcount)}:R>", monster_HP,
                                     monster_HP_MAX, actions=f"Monster Turn ends...", color=0xFFD800)
                    embed.add_field(name=f'{mname} Tried Attacking...', value="But they weren't able to attack anyone!",
                                    inline=False)
                    attacking = False
                    break
                t_dmg = random.randrange(10, 25)
                t_crit = random.randrange(1, 100)

                targetValid = False
                while not targetValid:
                    t_attacked = random.choice(validTargets)
                    if t_attacked not in targetList:
                        targetValid = True
                        targetList.append(t_attacked)

                attacked[t_attacked] = t_dmg
                hitpoints[t_attacked] = hitpoints[t_attacked] - t_dmg
                if hitpoints[t_attacked] < 0:
                    t_dmg = t_dmg + hitpoints[t_attacked]
                    hitpoints[t_attacked] = 0
                user = await bot.get_or_fetch_user(t_attacked)
                attackstring = f'{attackstring}{user.name} for {t_dmg} Damage!\n'
                embed = await newEmbed(f"{mname} is taking their turn!", monster, f"...<t:{int(atk_time + 16 + atkcount)}:R>",
                                 monster_HP,
                                 monster_HP_MAX, actions=f"Turn ends...:", color=0xFFD800)
                embed.add_field(name=f'{mname} attacked:', value=attackstring, inline=False)
                await message.edit(embed=embed)
                await asyncio.sleep(1)
                atkcount -= 1
            await asyncio.sleep(15)
        elif monster_HP > 0:
            embed = await newEmbed(f"{mname} is taking their turn!", monster, f"...<t:{int(atk_time + 7 + atkcount)}:R>",
                             monster_HP,
                             monster_HP_MAX, actions=f"Turn Ends...", color=0xFFD800)
            embed.add_field(name=f'{mname} tried attacking!', value="But they weren't able to attack anyone!",
                            inline=False)
            # noinspection PyTypeChecker
            await message.edit(embed=embed, components=[
                disnake.ui.ActionRow(
                    disnake.ui.Button(label="🗡️ Attack", custom_id=f"attack_enemy", style=disnake.Color(4),
                                      disabled=True),
                    disnake.ui.Button(label="💊 Heal", custom_id=f"heal_player", style=disnake.Color(1),
                                      disabled=True),
                    disnake.ui.Button(label="🕊️ Mercy", custom_id=f"mercy", style=disnake.Color(3),
                                      disabled=True))])
            await asyncio.sleep(5)
        action_to_process = True

        battleTime = int(time.time())
        if turnCount < 10:
            turn = True
    await message.edit(components=None)
    if victory:

        if len(player_mercy) >= spare_min:
            spared = True
        else:
            spared = False

        fight_average.append(1)
        if spared: str_wintype = "spared";
        else: str_wintype = "defeated"
        msg = f"{mname} was {str_wintype}!"
        vEmbed = await newEmbed(msg, monster, 0, 0, monster_HP_MAX, actions=False)
        reg_c = random.randrange(300, 650)

        if not spared:
            bestAttacker = None
            tmpDMG = 0
            tmpUSR = 0
            for i in dmgDone:
                if dmgDone[i] > tmpDMG and lastAttacker is not i:
                    tmpDMG = dmgDone[i]
                    tmpUSR = i
            user2 = await bot.get_or_fetch_user(tmpUSR)

            if tmpUSR != 0:
                user = await bot.get_or_fetch_user(lastAttacker)

                draw = random.randint(1, 20)
                if draw <= 11:
                    prize = db.award_random_prize(user2, "Battlebot", 1)
                elif draw <= 19:
                    prize = db.award_random_prize(user2, "Battlebot", 2)
                else:
                    prize = db.award_random_prize(user2, "Battlebot", 3)
                prize_data = db.get_prize(prize)

                vEmbed.add_field(name='Monster Defeated',
                                    value=f'{user.name} got the final hit! They have been awarded {reg_c} POINTs!\n{user2} did the most damage, with {tmpDMG} damage! They have been awarded with a {prize_data[1]}', inline=False)
            else:
                user = await bot.get_or_fetch_user(lastAttacker)
                vEmbed.add_field(name='Monster Defeated',
                                 value=f'{user.name} got the final hit! They have been awarded {reg_c} POINTs!',
                                 inline=False)
            loss = False
            addCandies(user, reg_c)
        else: # They spared the monster!
            reg_c = int(reg_c / 2)

            if random.randint(1, 100) >= 75: # someone gets a prize!
                lucky_player = random.choice(player_mercy)

                user2 = await bot.get_or_fetch_user(lucky_player)

                draw = random.randint(1, 20)
                if draw <= 11:
                    prize = db.award_random_prize(user2, "Battlebot", 1)
                elif draw <= 19:
                    prize = db.award_random_prize(user2, "Battlebot", 2)
                else:
                    prize = db.award_random_prize(user2, "Battlebot", 3)
                prize_data = db.get_prize(prize)
                prize_str = f"\n{user2.name} was given a {prize_data[1]} for their mercy!"
            else:
                prize_str = ""
            vEmbed.add_field(name='Monster Spared', value=f'{mname} was spared!\nAll players who showed MERCY have been rewarded with {reg_c} POINTs and have successfully recruited {mname}!{prize_str}', inline=False)
            loss = False

            for player in player_mercy:
                c_m = await bot.get_or_fetch_user(player)
                addCandies(c_m, reg_c)
                current_recruits = db.get_game_data("Battlebot", c_m)
                if current_recruits is None:
                    current_recruits = {}
                else:
                    current_recruits = current_recruits[0]
                    current_recruits = json.loads(current_recruits)

                temp_monster_data = enemy_list[mname]

                rec_str = f"{temp_monster_data['emote']} - \"{mname}\""

                if mname in current_recruits:
                    current_recruits[rec_str] = current_recruits[rec_str] + 1
                else:
                    current_recruits[rec_str] = 1
                db.set_game_data("Battlebot", c_m, json.dumps(current_recruits))

    else:
        fight_average.append(0)
        msg = f"{mname} got away!"
        vEmbed = await newEmbed(msg, monster, -1, monster_HP, monster_HP_MAX, actions=False)
        vEmbed.add_field(name=f'{mname} Escaped', value=f'{mname} escaped, so nobody was paid! :(', inline=False)
        loss = True

    await message.edit(embed=vEmbed)

    old_userList = hitpoints.items()
    bot.remove_listener(on_battle_press)


async def attack(action, player_hp):
    global dmgDone, lastAttacker
    lastAttacker = action.author.id
    avg = sum(fight_average) / len(fight_average)
    attackLow = 95
    attackHigh = 175
    attackDmg = random.randrange(attackLow, attackHigh)

    if player_hp < 25:
        attackDmg = int(attackDmg * 1.35)
    elif player_hp < 50:
        attackDmg = int(attackDmg * 1.25)

    # extra damage if mercy...
    if action.author.id in player_mercy:
        attackDmg = int(attackDmg * 1.50) # wowzers

    n_C = random.randrange(30, 80)

    if avg < 0.3:
        rareChance = 80
    else:
        rareChance = 98

    c_C = getCandies(action.author)

    HPLoss = random.randrange(0, 35)
    player_hp = player_hp - HPLoss

    if HPLoss > 30:
        attackDmg = int(attackDmg * 1.10)

    crit = random.randrange(1, 100)

    if avg < 0.3:
        crit = crit * 1.25

    if crit >= 95:
        attackDmg = attackDmg * 3
        pmEmbed = disnake.Embed(title="You attack the enemy!", color=0xFFD800)
        pmEmbed.description = f"**CRITICAL HIT!** You deal {attackDmg} damage!\nYou won {n_C} POINTs for your mighty blow!"
        player_hp = player_hp + HPLoss
        pmEmbed.set_image(
            url='https://media.discordapp.net/attachments/669077343482019870/902003156924379156/tumblr_m0biocwpJC1rnm2iko1_500.png')
    else:
        pmEmbed = disnake.Embed(title="You attack the enemy!", color=0xD95249)

        if player_hp < 0:
            HPLoss = HPLoss + player_hp
            player_hp = 0

        if HPLoss == 0:
            dmgText = ' and take no'
        else:
            dmgText = f', but take {HPLoss}'

        pmEmbed.description = f'You deal {attackDmg} damage{dmgText} damage in return.\nYou currently have **{player_hp}/100** health remaining.\nYou were awarded {n_C} POINTs for your attack.'
    await action.send(embed=pmEmbed, ephemeral=True)

    addCandies(action.author, n_C)

    if action.author.id not in dmgDone:
        dmgDone[action.author.id] = attackDmg
    else:
        dmgDone[action.author.id] = dmgDone[action.author.id] + attackDmg
    print(dmgDone)

    return attackDmg, player_hp


async def heal(action, hitpoints):
    avg = sum(fight_average) / len(fight_average)

    if avg > 0.85:
        healLow = 10
        healHigh = 45
    else:
        healLow = 20
        healHigh = 60

    heal = random.randrange(healLow, healHigh)

    if hitpoints > 75:
        heal = int(heal * 0.75)

    hlEmbed = disnake.Embed(title="You take a moment to heal your wounds.", color=0x59A361)
    hitpoints = min(100, (hitpoints + heal))
    if hitpoints == 69:
        hitpoints = 70
        heal = heal + 1
    if hitpoints == 100:
        hitpoints = 100
        hlEmbed.description = "You were fully healed!\nYou have **100/100** health remaining."
    else:
        hlEmbed.description = f"You were healed by {heal} hitpoints.\nYou now have **{hitpoints}/100** health remaining."

    await action.send(embed=hlEmbed, ephemeral=True)

    return hitpoints

