import pygame, sys, os, json, random, math

WIDTH, HEIGHT = 1280, 720
FPS = 60
SAVE_FILENAME = "save.json"

COL_UI=(230,235,245); COL_SUB=(200,210,225); COL_ACC=(120,170,255); COL_GREEN=(130,230,170); COL_RED=(245,95,120)
FONT_NAME=None

def project_dir(): return os.path.dirname(os.path.abspath(__file__))
def load_img(path): return pygame.image.load(os.path.join(project_dir(), "assets", path)).convert_alpha()

def load_save():
    path=os.path.join(project_dir(), SAVE_FILENAME)
    if not os.path.exists(path):
        data={"version":1,"essence":0,"upgrades":{"max_hp":0,"energy":0},"unlocks":{"beam_card":False},"relics_unlocked":[]}
        save_save(data); return data
    with open(path,"r",encoding="utf-8") as f: return json.load(f)
def save_save(data):
    path=os.path.join(project_dir(), SAVE_FILENAME)
    with open(path,"w",encoding="utf-8") as f: json.dump(data,f,indent=2)

ASSETS={}
def load_assets():
    ASSETS["bg"]=load_img("ui/background.png"); ASSETS["panel"]=load_img("ui/panel.png")
    ASSETS["btn_idle"]=load_img("ui/button_idle.png"); ASSETS["btn_hover"]=load_img("ui/button_hover.png"); ASSETS["btn_pressed"]=load_img("ui/button_pressed.png")
    ASSETS["card_frame"]=load_img("cards/frame.png")
    for icon in ["sword","shield","energy","draw","beam","heart","shop","coin"]:
        ASSETS["icon_"+icon]=load_img(f"icons/{icon}.png")
    for e in ["bandit","raptor","guardian"]:
        ASSETS["enemy_"+e]=load_img(f"enemies/{e}.png")
    ASSETS["glow"]=load_img("fx/glow.png"); ASSETS["particle"]=load_img("fx/particle.png")

def clamp(v,a,b): return max(a, min(b, v))
def ease_out_quad(t): return 1-(1-t)*(1-t)

class Button:
    def __init__(self,x,y,w,h,text,font,on_click=None):
        self.rect=pygame.Rect(x,y,w,h); self.text=text; self.font=font; self.on_click=on_click; self.state="idle"
    def draw(self,s):
        img=ASSETS["btn_idle"] if self.state=="idle" else ASSETS["btn_hover"] if self.state=="hover" else ASSETS["btn_pressed"]
        s.blit(img, self.rect.topleft); t=self.font.render(self.text, True, COL_UI); s.blit(t,(self.rect.centerx-t.get_width()//2, self.rect.centery-t.get_height()//2))
    def update(self, events):
        mx,my=pygame.mouse.get_pos(); inside=self.rect.collidepoint(mx,my); self.state="hover" if inside else "idle"
        for e in events:
            if inside and e.type==pygame.MOUSEBUTTONDOWN and e.button==1: self.state="pressed"
            if inside and e.type==pygame.MOUSEBUTTONUP and e.button==1:
                if self.on_click: self.on_click()


class Card:
    def __init__(self, name, cost, desc, icon,
                 damage=0, block=0, draw=0, energy=0, heal=0, piercing=False,
                 apply_vuln=0, apply_weak=0, apply_poison=0,
                 gain_rage=0, gain_thorns=0, gain_plated=0):
        self.name=name; self.cost=cost; self.desc=desc; self.icon=icon
        self.damage=damage; self.block=block; self.draw=draw; self.energy=energy; self.heal=heal; self.piercing=piercing
        # status effects
        self.apply_vuln=apply_vuln; self.apply_weak=apply_weak; self.apply_poison=apply_poison
        self.gain_rage=gain_rage; self.gain_thorns=gain_thorns; self.gain_plated=gain_plated
    def clone(self):
        return Card(self.name,self.cost,self.desc,self.icon,
                    self.damage,self.block,self.draw,self.energy,self.heal,self.piercing,
                    self.apply_vuln,self.apply_weak,self.apply_poison,
                    self.gain_rage,self.gain_thorns,self.gain_plated)


class CardLib:
    @staticmethod
    def pool(unlocks):
        p=[Card("Strike",1,"Inflige 6","sword",damage=6),
           Card("Heavy",2,"Inflige 18","sword",damage=18),
           Card("Defend",1,"Gain 5 block","shield",block=5),
           Card("Quick",1,"Block 3, Pioche 1","draw",block=3,draw=1),
           Card("Spark",0,"Pioche 2, +1 Energie","energy",draw=2,energy=1),
           Card("Soin",1,"Récupère 6 PV","heart",heal=6),
           Card("Soin+",2,"Récupère 12 PV","heart",heal=12),
           Card("Vulnérabilité",1,"Cible prend +50% dégâts (2 tours)","beam",apply_vuln=2),
           Card("Affaiblir",1,"Cible inflige -25% dégâts (2 tours)","draw",apply_weak=2),
           Card("Poison",1,"Applique 4 poison","energy",apply_poison=4),
           Card("Rage",1,"+50% dégâts ce tour","sword",gain_rage=1),
           Card("Épines",1,"Gagne Épines 3","shield",gain_thorns=3),
           Card("Plastron",2,"Gagne Plastron 3 par tour","shield",gain_plated=3)]
        if unlocks.get("beam_card",False): p.append(Card("Rayon",2,"16 perçant","beam",damage=16,piercing=True))
        return p
    @staticmethod
    def starter(unlocks):
        return [Card("Strike",1,"Inflige 6","sword",damage=6) for _ in range(5)] + [Card("Defend",1,"Gain 5","shield",block=5) for _ in range(5)]

class CardView:
    def __init__(self, card, rect):
        self.card=card; self.base_rect=pygame.Rect(rect); self.rect=pygame.Rect(rect)
        self.hover=0.0; self.playing=False; self.alpha=255; self.fly_t=0.0; self.fly_tot=0.45; self.fly_target=None; self.on_reach=None
    def update(self, dt):
        mx,my=pygame.mouse.get_pos(); hov=1.0 if self.rect.collidepoint(mx,my) else 0.0
        self.hover += (hov - self.hover) * min(1.0, dt*10)
        scale=1+0.06*self.hover; lift=10*self.hover; w,h=self.base_rect.size
        self.rect.width=int(w*scale); self.rect.height=int(h*scale); self.rect.centerx=self.base_rect.centerx; self.rect.y=self.base_rect.y - int(lift)
        if self.playing and self.fly_target:
            self.fly_t += dt/self.fly_tot; t=clamp(self.fly_t,0,1); t2=ease_out_quad(t); tx,ty=self.fly_target
            self.rect.centerx=int(self.rect.centerx+(tx-self.rect.centerx)*t2); self.rect.centery=int(self.rect.centery+(ty-self.rect.centery)*t2)
            self.alpha=int(255*(1-t))
            if t>=1.0:
                self.playing=False
                if self.on_reach: cb=self.on_reach; self.on_reach=None; cb()
    def draw(self,s,font,small):
        frame=pygame.transform.smoothscale(ASSETS["card_frame"], self.rect.size); 
        if self.alpha!=255: frame=frame.copy(); frame.set_alpha(self.alpha)
        s.blit(frame, self.rect.topleft)
        icon=ASSETS["icon_"+self.card.icon]; icon_sz=(int(self.rect.w*0.32), int(self.rect.w*0.32))
        s.blit(pygame.transform.smoothscale(icon, icon_sz), (self.rect.x+int(self.rect.w*0.07), self.rect.y+int(self.rect.h*0.06)))
        title=font.render(self.card.name, True, COL_UI); s.blit(title,(self.rect.x+int(self.rect.w*0.45), self.rect.y+int(self.rect.h*0.04)))
        cost=font.render(f"[{self.card.cost}]", True, COL_ACC); s.blit(cost,(self.rect.x+self.rect.w-cost.get_width()-int(self.rect.w*0.06), self.rect.y+int(self.rect.h*0.04)))
        desc=small.render(self.card.desc, True, (210,220,230)); s.blit(desc,(self.rect.x+int(self.rect.w*0.07), self.rect.y+int(self.rect.h*0.38)))

class Enemy:
    def __init__(self,name,max_hp,img_key,pattern):
        self.name=name; self.max_hp=max_hp; self.hp=max_hp; self.block=0; self.img_key=img_key; self.pattern=pattern; self.turn=0; self.intent=("atk",6)
        self.status={"poison":0,"weak":0,"vuln":0,"thorns":0,"plated":0}
    def choose_intent(self): self.intent=self.pattern[self.turn%len(self.pattern)]; self.turn+=1
    def take_damage(self,dmg,piercing=False, source_is_player=True):
        if self.status.get("vuln",0)>0: dmg=int(dmg*1.5)
        if piercing: self.hp-=dmg
        else:
            ab=min(self.block,dmg); self.block-=ab; self.hp -= max(0,dmg-ab)
        self.hp=max(0,self.hp)

def enemy_for_floor(f):
    if f <= 9:
        base_hp = 40 + f*10
        atk1 = 5 + f
        atk2 = 7 + 2*f
        defend = 5 + f
        t = f % 4
        if t == 1:
            e = Enemy(f"Bandit {f}", base_hp, "enemy_bandit", [("atk", atk1), ("def", defend), ("atk", atk2), ("atk", atk2+2)])
        elif t == 2:
            e = Enemy(f"Raptor {f}", base_hp+10, "enemy_raptor", [("atk", atk2), ("atk", atk1), ("def", defend+2), ("atk", atk2+2)])
            e.status["thorns"]=1 + f//3
        elif t == 3:
            e = Enemy(f"Mimic {f}", base_hp+5, "enemy_guardian", [("def", defend), ("atk", atk2), ("atk", atk2+3), ("def", defend+2)])
        else:
            e = Enemy(f"Sentinelle {f}", base_hp+20, "enemy_guardian", [("def", defend+3), ("atk", atk2), ("atk", atk2+3), ("atk", atk2+4)])
            e.status["plated"]=1 + f//4
        return e
    boss = Enemy("ARCHON (Boss)", 220, "enemy_guardian", [("def", 16), ("atk", 18), ("atk", 22), ("atk", 26), ("def", 20), ("atk", 28)])
    boss.status["thorns"]=3; boss.status["plated"]=3
    return boss

class Player:
    def __init__(self, save):
        self.up_hp=save["upgrades"]["max_hp"]; self.up_energy=save["upgrades"]["energy"]
        self.max_hp=70 + self.up_hp*20; self.hp=self.max_hp; self.energy_base=3 + self.up_energy; self.energy=self.energy_base; self.block=0
        self.status={"rage":0,"thorns":0,"plated":0}
        self.deck=[c.clone() for c in CardLib.starter(save["unlocks"])]; random.shuffle(self.deck)
        self.discard=[]; self.hand=[]; self.draw_pile=list(self.deck); self.turn_draw=5
    def rebuild_piles_full(self):
        self.discard=[]; self.hand=[]; self.draw_pile=[c.clone() for c in self.deck]; random.shuffle(self.draw_pile)
    def draw(self,n):
        for _ in range(n):
            if not self.draw_pile:
                self.draw_pile=self.discard; self.discard=[]; random.shuffle(self.draw_pile)
            if not self.draw_pile: return
            self.hand.append(self.draw_pile.pop())
    def new_turn(self):
        self.energy=self.energy_base; self.block=0
        if self.status.get("plated",0)>0: self.block+=self.status["plated"]
        self.draw(self.turn_draw)
    def play_card(self,idx,enemy):
        if idx<0 or idx>=len(self.hand): return False
        c=self.hand[idx]
        if c.cost>self.energy: return False
        self.energy-=c.cost
        if c.damage>0:
            dmg=c.damage
            if self.status.get("rage",0)>0: dmg=int(dmg*1.5)
            if hasattr(self, "run_relics") and "BattleFury" in self.run_relics: dmg+=2
            enemy.take_damage(dmg, piercing=c.piercing, source_is_player=True)
        if c.block>0: self.block+=c.block
        if c.draw>0: self.draw(c.draw)
        if c.energy>0: self.energy+=c.energy
        if hasattr(c, "heal") and c.heal>0: self.hp=min(self.max_hp, self.hp + c.heal)
        if c.apply_vuln>0: enemy.status["vuln"]=min(99, enemy.status.get("vuln",0)+c.apply_vuln)
        if c.apply_weak>0: enemy.status["weak"]=min(99, enemy.status.get("weak",0)+c.apply_weak)
        if c.apply_poison>0: enemy.status["poison"]=min(999, enemy.status.get("poison",0)+c.apply_poison)
        if c.gain_rage>0: self.status["rage"]=max(self.status.get("rage",0), c.gain_rage)
        if c.gain_thorns>0: self.status["thorns"]=min(99, self.status.get("thorns",0)+c.gain_thorns)
        if c.gain_plated>0: self.status["plated"]=min(99, self.status.get("plated",0)+c.gain_plated)
        self.discard.append(c); del self.hand[idx]; return True
    def end_turn(self, enemy):
        it,val=enemy.intent
        if it=="atk":
            dmg=val
            if enemy.status.get("weak",0)>0: dmg=int(dmg*0.75)
            if self.block>=dmg: self.block-=dmg
            else: dmg-=self.block; self.block=0; self.hp-=dmg
            if self.status.get("thorns",0)>0 and dmg>0:
                enemy.take_damage(self.status["thorns"], piercing=True, source_is_player=False)
                # visual feedback
                tx,ty=  self.run.screen_w-300 if hasattr(self.run,"screen_w") else 980, 150
                try:
                    self.run.dmg_numbers.append(DamageText(tx,ty,f"-{self.status['thorns']} (épines)",(255,190,190)))
                except Exception:
                    pass
        elif it=="def": enemy.block+=val
        self.status["rage"]=0
        self.discard.extend(self.hand); self.hand.clear()

class Particle:
    def __init__(self,x,y,vx,vy,life): self.x=x; self.y=y; self.vx=vx; self.vy=vy; self.life=life; self.max_life=life
    def update(self,dt): self.x+=self.vx*dt; self.y+=self.vy*dt; self.life-=dt; return self.life>0
    def draw(self,s): img=ASSETS["particle"]; a=int(255*clamp(self.life/self.max_life,0,1)); surf=img.copy(); surf.set_alpha(a); s.blit(surf,(int(self.x),int(self.y)))
class DamageText:
    def __init__(self,x,y,txt,col): self.x=x; self.y=y; self.t=0.0; self.txt=txt; self.col=col
    def update(self,dt): self.t+=dt; return self.t<1.0
    def draw(self,s,font): y=self.y-int(40*ease_out_quad(clamp(self.t,0,1))); a=int(255*(1-clamp(self.t,0,1))); t=font.render(self.txt, True, self.col); t.set_alpha(a); s.blit(t,(self.x,y))

class Run:
    def __init__(self, save):
        self.save=save; self.floor=1; self.player=Player(save); self.enemy=enemy_for_floor(self.floor); self.enemy.choose_intent()
        self.done=False; self.win=False; self.particles=[]; self.dmg_numbers=[]; self.message=""; self.player.new_turn()
        # relics per run
        self.relics=[]; pool=self.save.get("relics_unlocked",[])
        if pool: self.relics=[random.choice(pool)]
        self.player.run_relics=self.relics
        if "TurtleShell" in self.relics: self.player.status["plated"]+=2
        if "AdrenalGland" in self.relics: self.player.turn_draw+=1
        if "AncientCoin" in self.relics: self.player.energy+=1
    def update(self,dt):
        self.particles=[p for p in self.particles if p.update(dt)]
        self.dmg_numbers=[d for d in self.dmg_numbers if d.update(dt)]
    def end_turn(self):
        self.player.end_turn(self.enemy)
        # end of round: poison ticks, decay statuses on enemy
        if self.enemy.status.get("poison",0)>0:
            dmg=self.enemy.status["poison"]; self.enemy.take_damage(dmg, piercing=True); self.enemy.status["poison"]=max(0,self.enemy.status["poison"]-1)
            # feedback
            tx = getattr(self, "screen_w", 1280) - 300; ty = 150
            self.dmg_numbers.append(DamageText(tx, ty, f"-{dmg} (poison)", (170,255,170)))
        for k in ["vuln","weak"]:
            if self.enemy.status.get(k,0)>0: self.enemy.status[k]-=1
        if self.player.hp<=0: self.done=True; self.win=False; return
        if self.enemy.hp<=0:
            if self.floor>=10: self.done=True; self.win=True; return
            else:
                self.floor+=1; self.player.block=0
                if self.floor in (4,7,9): return "event"
                self.enemy=enemy_for_floor(self.floor); self.enemy.choose_intent(); return "reward"
        self.enemy.choose_intent(); self.player.new_turn()
    def essence_gain(self):
        base = 12 * (self.floor - 1)
        if self.win: base += 120
        return base

STATE_MENU=0; STATE_SHOP=1; STATE_RUN=2; STATE_REWARD=3; STATE_GAMEOVER=4; STATE_EVENT=5

class Game:
    def __init__(self):
        pygame.init(); pygame.display.set_caption("DeckLite — Roguelite Deckbuilder")
        self.screen=pygame.display.set_mode((WIDTH,HEIGHT), pygame.RESIZABLE)
        self.clock=pygame.time.Clock(); self.font=pygame.font.Font(FONT_NAME,26); self.small=pygame.font.Font(FONT_NAME,20); self.big=pygame.font.Font(FONT_NAME,40)
        load_assets(); self.save=load_save(); 
        if "relics_unlocked" not in self.save: self.save["relics_unlocked"]=[]
        self.state=STATE_MENU; self.run=None; self.reward_options=[]; self.reward_rects=[]
        self.card_views=[]; self.hand_area=pygame.Rect(80, HEIGHT-300, WIDTH-240, 260); self.end_button=Button(WIDTH-200, HEIGHT-120, 160,60,"Fin", self.font, on_click=self.on_end_turn)
        self.show_draw=False; self.deck_button=Button(0, 0, 120, 44, "Deck", self.small, on_click=self.toggle_draw_panel)
    # Utilities
    def draw_bg(self):
        sw,sh=self.screen.get_size(); self.screen.blit(pygame.transform.smoothscale(ASSETS["bg"],(sw,sh)),(0,0))
    def layout_hand(self):
        self.card_views=[]; 
        if not self.run: return
        r=self.hand_area; n=max(1, len(self.run.player.hand)); gap=20; ratio=300/420; max_ch=int(self.screen.get_height()*0.5)
        def size_for(nc):
            cw_n=min(300, max(140, (r.w - gap*(nc-1))//nc)); ch_n=int(cw_n/ratio)
            if ch_n>max_ch: ch_n=max_ch; cw_n=int(ch_n*ratio)
            return cw_n, ch_n
        cw5,ch5=size_for(5); cw,ch=size_for(n); cw=min(cw,cw5); ch=min(ch,ch5)
        total_w=n*cw + (n-1)*gap; start_x=r.x + max(0,(r.w-total_w)//2); y=r.y + max(0,(r.h-ch)//2)
        for i,c in enumerate(self.run.player.hand): self.card_views.append(CardView(c, (start_x + i*(cw+gap), y, cw, ch)))

    # --- Status badges UI ---
    def draw_status_badges(self, x, y, statuses, who="enemy"):
        # Draw small rounded badges like "Po 3", "Vu 2", "Wk 1", "Rg", "Th 3", "Pl 2"
        # Colors per status
        col_map = {
            "poison": (160, 255, 160),
            "vuln": (255, 200, 160),
            "weak": (200, 200, 255),
            "thorns": (255, 180, 180),
            "plated": (200, 255, 200),
            "rage": (255, 220, 120),
        }
        keys = ["poison","vuln","weak","thorns","plated"]
        if who=="player":
            keys = ["rage","thorns","plated"]
        pad=8; gap=6; cx=x
        for k in keys:
            v = statuses.get(k,0)
            if k=="rage":
                if statuses.get("rage",0)>0: label="Rg"; col=col_map["rage"]
                else: continue
            else:
                if v<=0: continue
                label = ("Po" if k=="poison" else "Vu" if k=="vuln" else "Wk" if k=="weak" else "Th" if k=="thorns" else "Pl") + f" {v}"
                col = col_map[k]
            txt = self.small.render(label, True, (20,22,32))
            w = txt.get_width()+pad*2; h = txt.get_height()+4
            surf = pygame.Surface((w,h), pygame.SRCALPHA)
            pygame.draw.rect(surf, col, (0,0,w,h), border_radius=8)
            pygame.draw.rect(surf, (40,44,60), (0,0,w,h), 1, border_radius=8)
            surf.blit(txt,(pad,2))
            self.screen.blit(surf,(cx,y))
            cx += w + gap

    # Draw helpers
    def draw_enemy_panel(self):
        pnl=pygame.transform.smoothscale(ASSETS["panel"], (self.screen.get_width()-160, 200)); self.screen.blit(pnl,(80,40))
        e=self.run.enemy; self.screen.blit(pygame.transform.smoothscale(ASSETS[e.img_key], (360,220)), (self.screen.get_width()-480, 20))
        self.screen.blit(self.big.render(e.name, True, COL_UI),(100,60))
        self.screen.blit(self.font.render(f"PV: {e.hp}/{e.max_hp}   Block: {e.block}", True, COL_SUB),(100,100))
        it=e.intent; icon=ASSETS["icon_sword"] if it[0]=="atk" else ASSETS["icon_shield"]
        self.screen.blit(pygame.transform.smoothscale(icon,(48,48)),(100,140))
        self.screen.blit(self.font.render(("Attaque " if it[0]=='atk' else "Défense ")+str(it[1]), True, COL_ACC),(160,148))
        # status badges
        self.draw_status_badges(100, 172, e.status, who="enemy")
    def draw_player_panel(self):
        pnl=pygame.transform.smoothscale(ASSETS["panel"], (self.screen.get_width()-160, 120)); self.screen.blit(pnl,(80,260))
        p=self.run.player; self.screen.blit(self.font.render(f"PV: {p.hp}/{p.max_hp}   Block: {p.block}   Énergie: {p.energy}", True, COL_GREEN),(100,300))
        if hasattr(self.run, "relics") and self.run.relics:
            txt = "Relique: " + ", ".join(self.run.relics)
            self.screen.blit(self.small.render(txt, True, COL_SUB),(100,332))
    def draw_hand(self, dt, events):
        for cv in self.card_views: cv.update(dt)
        for cv in sorted(self.card_views, key=lambda x: x.rect.y): cv.draw(self.screen, self.font, self.small)
    def draw_drawpile_panel(self):
        if not self.run: return
        dp=self.run.player.draw_pile; discard=self.run.player.discard
        pool = dp if len(dp)>0 else discard
        source_label = "Pioche" if len(dp)>0 else "Défausse (après mélange)"
        total=len(pool); width=420; from collections import Counter
        counts=Counter([c.name for c in pool]) if total>0 else {}; rows=sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
        max_rows=12; vis=rows[:max_rows]; height=120 + 24*max(1,len(vis)); x=20; y=70
        pnl=pygame.Surface((width,height), pygame.SRCALPHA); pnl.fill((20,22,32,230)); pygame.draw.rect(pnl,(90,100,130),(0,0,width,height),2,border_radius=10)
        pnl.blit(self.font.render("Deck piochable", True, COL_UI),(14,10)); pnl.blit(self.small.render(f"Prochain tirage depuis: {source_label}", True, COL_SUB),(14,44))
        if total==0: pnl.blit(self.small.render("(aucune carte à tirer)", True, COL_SUB),(14,72))
        else:
            samples={}; 
            for c in pool:
                if c.name not in samples: samples[c.name]=c
            yoff=72
            for name,cnt in vis:
                prob=cnt/total*100.0; icon_key="icon_"+samples[name].icon; icon=pygame.transform.smoothscale(ASSETS[icon_key], (20,20))
                pnl.blit(icon,(14,yoff+2)); pnl.blit(self.small.render(f"{name}", True, COL_UI),(40,yoff))
                pnl.blit(self.small.render(f"x{cnt}", True, COL_SUB),(210,yoff)); pnl.blit(self.small.render(f"{prob:5.1f}%", True, COL_ACC),(270,yoff)); yoff+=24
            if len(rows)>max_rows: pnl.blit(self.small.render(f"... et {len(rows)-max_rows} autres", True, COL_SUB),(14,height-48))
            pnl.blit(self.small.render(f"Total cartes dans la source: {total}", True, COL_SUB),(14,height-28))
        dp_txt=self.small.render(f"Pioche: {len(dp)} | Défausse: {len(discard)}", True, COL_SUB); pnl.blit(dp_txt,(width - dp_txt.get_width() - 14, 10))
        self.screen.blit(pnl,(x,y))
    # Scenes
    def draw_menu(self, events):
        self.draw_bg(); title=self.big.render("DECKLITE — ROGUELITE DECKBUILDER", True, COL_UI)
        self.screen.blit(title,(self.screen.get_width()//2 - title.get_width()//2, 90))
        start=Button(self.screen.get_width()//2-110,220,220,70,"Démarrer",self.font,on_click=self.start_run)
        shop=Button(self.screen.get_width()//2-110,310,220,70,"Boutique",self.font,on_click=self.goto_shop)
        reset=Button(self.screen.get_width()//2-110,400,220,70,"Réinitialiser",self.font,on_click=self.reset_save)
        for b in [start,shop,reset]: b.update(events); b.draw(self.screen)
        ess=self.font.render(f"Essence: {self.save['essence']}", True, COL_ACC); self.screen.blit(ess,(self.screen.get_width()-ess.get_width()-40,30))
    def draw_event(self, events):
        self.draw_bg(); title=self.big.render("Événement", True, COL_UI)
        self.screen.blit(title,(self.screen.get_width()//2 - title.get_width()//2, 80))
        opts=[("Se reposer","+25% PV (arrondi)", "rest"),
              ("Trouver une relique","-8 PV, gagnez 1 relique", "relic"),
              ("Purifier","Retirer une carte basique", "purge")]
        self.event_rects=[]; y=200
        for name,desc,key in opts:
            pnl=pygame.transform.smoothscale(ASSETS["panel"], (900,90)); self.screen.blit(pnl,(self.screen.get_width()//2-450,y))
            self.screen.blit(self.font.render(name, True, COL_UI),(self.screen.get_width()//2-420, y+12))
            self.screen.blit(self.small.render(desc, True, COL_SUB),(self.screen.get_width()//2-420, y+50))
            self.event_rects.append((pygame.Rect(self.screen.get_width()//2-450,y,900,90), key)); y+=110
        back=Button(self.screen.get_width()//2-110, y+20, 220, 60, "Continuer", self.font, on_click=self.event_continue); back.update(events); back.draw(self.screen)
    def draw_run(self, dt, events):
        # store for feedback positioning
        if self.run:
            self.run.screen_w, self.run.screen_h = self.screen.get_size()
        self.draw_bg(); self.draw_enemy_panel(); self.draw_player_panel()
        sw,sh=self.screen.get_size(); self.end_button.rect.topleft=(sw-200, sh-120)
        pygame.draw.rect(self.screen,(22,24,34), self.hand_area, border_radius=12); self.draw_hand(dt, events)
        self.end_button.update(events); self.end_button.draw(self.screen)
        sw,sh=self.screen.get_size()
        self.deck_button.rect.topleft = (sw-200, 310)
        self.deck_button.update(events); self.deck_button.draw(self.screen)
        if self.show_draw: self.draw_drawpile_panel()
        for p in self.run.particles: p.draw(self.screen)
        for d in self.run.dmg_numbers: d.draw(self.screen, self.font)
        if self.run.done:
            gained=self.run.essence_gain(); overlay=pygame.Surface((sw,sh), pygame.SRCALPHA); overlay.fill((0,0,0,160))
            self.screen.blit(overlay,(0,0)); head=self.big.render("VICTOIRE" if self.run.win else "DÉFAITE", True, COL_UI)
            self.screen.blit(head,(sw//2 - head.get_width()//2, sh//2 - 90)); ess=self.font.render(f"+{gained} Essence", True, COL_ACC)
            self.screen.blit(ess,(sw//2 - ess.get_width()//2, sh//2 - 40)); press=self.small.render("[ENTREE] Continuer", True, COL_SUB)
            self.screen.blit(press,(sw//2 - press.get_width()//2, sh//2 + 20))
    def draw_reward(self, events):
        self.draw_bg(); title=self.big.render("Récompense: Choisissez une carte", True, COL_UI)
        self.screen.blit(title,(self.screen.get_width()//2 - title.get_width()//2, 80)); cw,ch=300,420; gap=40
        total=3*cw + 2*gap; x0=self.screen.get_width()//2 - total//2; y=170; self.reward_rects=[]
        for i,c in enumerate(self.reward_options):
            rect=pygame.Rect(x0 + i*(cw+gap), y, cw, ch); self.reward_rects.append(rect); CardView(c, rect).draw(self.screen, self.font, self.small)
        b=Button(self.screen.get_width()//2-110, y+ch+40, 220, 60, "Passer", self.font, on_click=self.skip_reward); b.update(events); b.draw(self.screen)
    def draw_shop(self, events):
        self.draw_bg(); title=self.big.render("BOUTIQUE MÉTA", True, COL_UI); self.screen.blit(title,(self.screen.get_width()//2 - title.get_width()//2, 80))
        ess=self.font.render(f"Essence: {self.save['essence']}", True, COL_ACC); self.screen.blit(ess,(self.screen.get_width()-ess.get_width()-40,30))
        items=[("PV+", f"Niveau {self.save['upgrades']['max_hp']}  |  Prix {self.cost_hp()}", "hp","heart"),
               ("Énergie+", f"Niveau {self.save['upgrades']['energy']}  |  Prix {self.cost_energy()}", "energy","energy"),
               ("Débloquer Carte Rayon", "Carte rare perçante  |  Prix {}".format(self.cost_beam()) if not self.save['unlocks']['beam_card'] else "DÉJÀ DÉBLOQUÉ", "beam","beam"),
               ("Débloquer Reliques", "Ajoute des reliques au pool de run  |  Prix {}".format(self.cost_relic()), "relic","coin")]
        self.shop_rects=[]; y=200
        for name,txt,key,icon in items:
            pnl=pygame.transform.smoothscale(ASSETS["panel"], (900,90)); self.screen.blit(pnl,(self.screen.get_width()//2-450,y))
            ic=pygame.transform.smoothscale(ASSETS["icon_"+icon],(56,56)); self.screen.blit(ic,(self.screen.get_width()//2-420, y+18))
            self.screen.blit(self.font.render(name, True, COL_UI),(self.screen.get_width()//2-350, y+12))
            self.screen.blit(self.small.render(txt, True, COL_SUB),(self.screen.get_width()//2-350, y+50))
            self.shop_rects.append((pygame.Rect(self.screen.get_width()//2-450,y,900,90), key)); y+=110
        back=Button(self.screen.get_width()//2-110, y+20, 220, 60, "Retour", self.font, on_click=self.goto_menu); back.update(events); back.draw(self.screen)
    def draw_gameover(self, events):
        self.draw_bg(); head=self.big.render("VICTOIRE" if self.run.win else "DÉFAITE", True, COL_UI); self.screen.blit(head,(self.screen.get_width()//2 - head.get_width()//2, 140))
        ess=self.font.render(f"Essence gagnée: {self.run.essence_gain()}", True, COL_ACC); self.screen.blit(ess,(self.screen.get_width()//2 - ess.get_width()//2, 220))
        menu=Button(self.screen.get_width()//2-250, 340, 220, 60, "Menu", self.font, on_click=self.goto_menu_state)
        shop=Button(self.screen.get_width()//2+30, 340, 220, 60, "Boutique", self.font, on_click=self.goto_shop_state)
        for b in [menu, shop]: b.update(events); b.draw(self.screen)
    # Events
    def handle_event_click(self, pos):
        for rect,key in self.event_rects:
            if rect.collidepoint(pos):
                if key=="rest":
                    heal = max(1, self.run.player.max_hp//4)
                    self.run.player.hp = min(self.run.player.max_hp, self.run.player.hp + heal)
                elif key=="relic":
                    self.run.player.hp = max(1, self.run.player.hp - 8)
                    pool = ["TurtleShell","AdrenalGland","BattleFury","AncientCoin"]
                    pick = random.choice(pool)
                    if hasattr(self.run, "relics"): self.run.relics.append(pick)
                elif key=="purge":
                    names=["Strike","Defend"]
                    removed=False
                    for nm in names:
                        for i,c in enumerate(self.run.player.deck):
                            if c.name==nm:
                                del self.run.player.deck[i]; removed=True; break
                        if removed: break
    def event_continue(self):
        self.run.enemy=enemy_for_floor(self.run.floor); self.run.enemy.choose_intent(); self.state=STATE_RUN
        self.run.player.rebuild_piles_full(); self.run.player.new_turn(); self.layout_hand()
    # Actions / handlers
    def start_run(self):
        self.run=Run(self.save); self.state=STATE_RUN; self.hand_area=pygame.Rect(80, self.screen.get_height()-300, self.screen.get_width()-240, 260); self.layout_hand()
    def goto_shop(self): self.state=STATE_SHOP
    def reset_save(self): self.save={"version":1,"essence":0,"upgrades":{"max_hp":0,"energy":0},"unlocks":{"beam_card":False},"relics_unlocked":[]}; save_save(self.save)
    def on_end_turn(self):
        if self.state!=STATE_RUN: return
        res=self.run.end_turn()
        if res=="event":
            self.state=STATE_EVENT
        elif res=="reward":
            pool=CardLib.pool(self.save["unlocks"]); self.reward_options=random.sample(pool,3); self.state=STATE_REWARD
        self.layout_hand()
    def skip_reward(self):
        self.state=STATE_RUN; self.run.player.rebuild_piles_full(); self.run.player.new_turn(); self.layout_hand()
    def goto_menu(self): self.state=STATE_MENU
    def goto_menu_state(self): self.state=STATE_MENU
    def goto_shop_state(self): self.state=STATE_SHOP
    def cost_hp(self): lvl=self.save["upgrades"]["max_hp"]; return 24 + 12*lvl
    def cost_energy(self): lvl=self.save["upgrades"]["energy"]; return 120 + 60*lvl
    def cost_beam(self): return 200
    def cost_relic(self): return 180
    def handle_shop_click(self, pos):
        for rect,key in self.shop_rects:
            if rect.collidepoint(pos):
                if key=="hp":
                    c=self.cost_hp()
                    if self.save["essence"]>=c: self.save["essence"]-=c; self.save["upgrades"]["max_hp"]+=1; save_save(self.save)
                elif key=="energy":
                    c=self.cost_energy()
                    if self.save["essence"]>=c: self.save["essence"]-=c; self.save["upgrades"]["energy"]+=1; save_save(self.save)
                elif key=="beam":
                    if not self.save["unlocks"]["beam_card"]:
                        c=self.cost_beam()
                        if self.save["essence"]>=c: self.save["essence"]-=c; self.save["unlocks"]["beam_card"]=True; save_save(self.save)
                elif key=="relic":
                    c=self.cost_relic()
                    if self.save["essence"]>=c:
                        self.save["essence"]-=c
                        pool=["TurtleShell","AdrenalGland","BattleFury","AncientCoin"]
                        choices=[r for r in pool if r not in self.save.get("relics_unlocked",[])]
                        if not choices: choices=pool
                        pick=random.choice(choices)
                        self.save.setdefault("relics_unlocked",[]).append(pick); save_save(self.save)
    def handle_run_click(self, pos):
        if self.end_button.rect.collidepoint(pos): return
        if not self.card_views: return
        x,y=pos
        for i,cv in enumerate(self.card_views):
            if cv.rect.collidepoint(x,y):
                if i>=len(self.run.player.hand): return
                c=self.run.player.hand[i]
                if c.cost>self.run.player.energy: return
                tx,ty=self.screen.get_width()-300,150
                def on_hit(i=i, tx=tx, ty=ty):
                    if i < len(self.run.player.hand):
                        c2=self.run.player.hand[i]
                        if c2.damage>0:
                            for _ in range(10):
                                ang=random.random()*math.tau; sp=random.uniform(60,160)
                                self.run.particles.append(Particle(tx,ty, math.cos(ang)*sp, math.sin(ang)*sp, 0.5))
                            self.run.dmg_numbers.append(DamageText(tx,ty,f"-{c2.damage}",(255,210,210)))
                        if c2.block>0: self.run.dmg_numbers.append(DamageText(120,300,f"+{c2.block} block",(200,255,200)))
                        if hasattr(c2,"heal") and c2.heal>0: self.run.dmg_numbers.append(DamageText(120,280,f"+{c2.heal} PV",(180,255,180)))
                        if hasattr(c2,"apply_vuln") and getattr(c2,"apply_vuln",0)>0: self.run.dmg_numbers.append(DamageText(self.screen.get_width()-420, 180, f"Vuln +{c2.apply_vuln}", (255,220,160)))
                        if hasattr(c2,"apply_weak") and getattr(c2,"apply_weak",0)>0: self.run.dmg_numbers.append(DamageText(self.screen.get_width()-420, 200, f"Weak +{c2.apply_weak}", (200,200,255)))
                        if hasattr(c2,"apply_poison") and getattr(c2,"apply_poison",0)>0: self.run.dmg_numbers.append(DamageText(self.screen.get_width()-420, 160, f"Poison +{c2.apply_poison}", (160,255,160)))
                        if hasattr(c2,"gain_rage") and getattr(c2,"gain_rage",0)>0: self.run.dmg_numbers.append(DamageText(120, 260, f"Rage", (255,240,160)))
                        if hasattr(c2,"gain_thorns") and getattr(c2,"gain_thorns",0)>0: self.run.dmg_numbers.append(DamageText(120, 240, f"Épines +{c2.gain_thorns}", (255,200,200)))
                        if hasattr(c2,"gain_plated") and getattr(c2,"gain_plated",0)>0: self.run.dmg_numbers.append(DamageText(120, 220, f"Plastron +{c2.gain_plated}", (200,255,200)))
                        # extra particles for statuses
                        if c2.apply_vuln>0 or c2.apply_weak>0 or c2.apply_poison>0:
                            for _ in range(12):
                                ang=random.random()*6.283; sp=random.uniform(40,120)
                                self.run.particles.append(Particle(tx,ty, math.cos(ang)*sp, math.sin(ang)*sp, 0.6))
                        if c2.gain_rage>0 or c2.gain_thorns>0 or c2.gain_plated>0:
                            px,py=140,300
                            for _ in range(12):
                                ang=random.random()*6.283; sp=random.uniform(40,120)
                                self.run.particles.append(Particle(px,py, math.cos(ang)*sp, math.sin(ang)*sp, 0.6))
                        self.run.player.play_card(i, self.run.enemy); self.layout_hand()
                cv.playing=True; cv.fly_t=0.0; cv.alpha=255; cv.fly_target=(tx,ty); cv.on_reach=on_hit; return
    def toggle_draw_panel(self): self.show_draw = not self.show_draw
    def mainloop(self):
        while True:
            dt=self.clock.tick(FPS)/1000.0; events=pygame.event.get()
            for e in events:
                if e.type==pygame.QUIT: pygame.quit(); sys.exit(0)
                if e.type==pygame.VIDEORESIZE:
                    self.screen=pygame.display.set_mode((e.w,e.h), pygame.RESIZABLE)
                    global WIDTH,HEIGHT
                    WIDTH,HEIGHT=e.w,e.h
                    self.hand_area=pygame.Rect(80, HEIGHT-300, WIDTH-240, 260)
                    if self.state==STATE_RUN:
                        self.layout_hand()
                if self.state==STATE_RUN and e.type==pygame.MOUSEBUTTONDOWN and e.button==1: self.handle_run_click(e.pos)
                if self.state==STATE_EVENT and e.type==pygame.MOUSEBUTTONDOWN and e.button==1: self.handle_event_click(e.pos)
                if self.state==STATE_REWARD and e.type==pygame.MOUSEBUTTONDOWN and e.button==1:
                    for i,r in enumerate(self.reward_rects):
                        if r.collidepoint(e.pos):
                            self.run.player.deck.append(self.reward_options[i].clone()); self.run.player.rebuild_piles_full()
                            self.state=STATE_RUN; self.run.player.new_turn(); self.layout_hand()
                if self.state==STATE_SHOP and e.type==pygame.MOUSEBUTTONDOWN and e.button==1: self.handle_shop_click(e.pos)
            if self.state==STATE_RUN and self.run:
                self.run.update(dt)
                if self.run.done:
                    self.save["essence"]+=self.run.essence_gain(); save_save(self.save); self.state=STATE_GAMEOVER
            if self.state==STATE_MENU: self.draw_menu(events)
            elif self.state==STATE_SHOP: self.draw_shop(events)
            elif self.state==STATE_RUN: self.draw_run(dt, events)
            elif self.state==STATE_EVENT: self.draw_event(events)
            elif self.state==STATE_REWARD: self.draw_reward(events)
            elif self.state==STATE_GAMEOVER: self.draw_gameover(events)
            pygame.display.flip()

if __name__=="__main__":
    Game().mainloop()
