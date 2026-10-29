import random
import tkinter as tk
from tkinter import ttk


BOARD_SIZE = 10
CELL_COUNT = BOARD_SIZE * BOARD_SIZE
COURSES = [
	"Administração", "Administração Pública", "Agroindústria", "Agronomia",
	"Arquitetura e Urbanismo", "Biologia", "Biotecnologia", "Ciência da Computação",
	"Ciências Biológicas", "Ciências Contábeis", "Ciências Econômicas",
	"Ciências Sociais", "Computação", "Direito", "Educação do Campo",
	"Educação Escolar Quilombola", "Educação Física", "Educação Intercultural Indígena",
	"Engenharia Ambiental", "Engenharia Civil", "Engenharia de Alimentos",
	"Engenharia de Bioprocessos e Biotecnologia", "Engenharia Elétrica",
	"Engenharia Florestal", "Enfermagem", "Filosofia", "Física",
	"Geografia", "Gestão de Cooperativas", "História", "Inteligência Artificial",
	"Jornalismo", "Letras", "Letras - Libras", "Licenciatura Intercultural Indígena",
	"Matemática", "Medicina", "Medicina Veterinária", "Música", "Nutrição",
	"Pedagogia", "Psicologia", "Química", "Química Ambiental",
	"Relações Internacionais", "Segunda Licenciatura em Educação Bilíngue de Surdos",
	"Serviço Social", "Teatro", "Turismo Patrimonial e Socioambiental",
]
RELIGIONS = [
	"Católica", "Evangélica", "Espírita", "Umbanda/Candomblé",
	"Budista", "Judaica", "Tradições indígenas",
]
ORIGINS = [
	"Acre", "Alagoas", "Amapá", "Amazonas", "Bahia", "Ceará", "Distrito Federal",
	"Espírito Santo", "Goiás", "Maranhão", "Mato Grosso", "Mato Grosso do Sul",
	"Minas Gerais", "Pará", "Paraíba", "Paraná", "Pernambuco", "Piauí",
	"Rio de Janeiro", "Rio Grande do Norte", "Rio Grande do Sul", "Rondônia",
	"Roraima", "Santa Catarina", "São Paulo", "Sergipe", "Tocantins",
]
WEIGHTS = {"sexo": 0.10, "período": 0.15, "curso": 0.15, "religião": 0.30, "origem": 0.30}
ATTRIBUTE_COLORS = ["#397b72", "#d07a4d", "#567ca4", "#9875a6", "#b59842", "#6d8d52", "#c26467"]
BG = "#f2f3ed"
INK = "#202927"
MUTED = "#69746e"


def make_agent(agent_id):
	return {
		"id": agent_id,
		"sexo": random.choice(("Masculino", "Feminino")),
		"período": random.randint(1, 8),
		"curso": random.choice(COURSES),
		"religião": random.choice(RELIGIONS),
		"origem": random.choice(ORIGINS),
		"x": 0,
		"y": 0,
	}


def similarity(first, second):
	return sum(
		weight for attribute, weight in WEIGHTS.items()
		if first[attribute] == second[attribute]
	)


class CultureSimulation:
	def __init__(self, root):
		self.root = root
		self.root.title("Convergência | Simulação social")
		self.root.configure(bg=BG)
		self.root.minsize(850, 620)
		self.agents = []
		self.occupied = {}
		self.round = 0
		self.running = False
		self.after_id = None
		self.selected_id = None
		self.last_move = None
		self.cell_size = 54
		self._build_ui()
		self.reset()

	def _build_ui(self):
		style = ttk.Style()
		style.theme_use("clam")
		style.configure("TFrame", background=BG)
		style.configure("TLabel", background=BG, foreground=INK, font=("DejaVu Sans", 10))
		style.configure("Title.TLabel", font=("DejaVu Sans", 20, "bold"))
		style.configure("Sub.TLabel", foreground=MUTED, font=("DejaVu Sans", 10))
		style.configure("TButton", font=("DejaVu Sans", 10, "bold"), padding=(12, 8))
		style.configure("TSpinbox", padding=7)

		header = ttk.Frame(self.root, padding=(24, 20, 24, 10))
		header.pack(fill="x")
		ttk.Label(header, text="Convergência", style="Title.TLabel").pack(anchor="w")
		ttk.Label(header, text="Um experimento de afinidade, movimento e formação de grupos", style="Sub.TLabel").pack(anchor="w", pady=(4, 0))

		content = ttk.Frame(self.root, padding=(24, 10, 24, 24))
		content.pack(fill="both", expand=True)
		board_panel = ttk.Frame(content)
		board_panel.pack(side="left", fill="both", expand=True)
		self.canvas = tk.Canvas(board_panel, bg="#e5e9e1", highlightthickness=0, width=540, height=540)
		self.canvas.pack(fill="both", expand=True)
		self.canvas.bind("<Configure>", lambda _event: self.draw_board())
		self.canvas.bind("<Button-1>", self._select_cell)

		side = ttk.Frame(content, width=250, padding=(22, 0, 0, 0))
		side.pack(side="right", fill="y")
		side.pack_propagate(False)

		ttk.Label(side, text="SIMULAÇÃO", foreground=MUTED, font=("DejaVu Sans", 9, "bold")).pack(anchor="w", pady=(2, 9))
		ttk.Label(side, text="Agentes no tabuleiro").pack(anchor="w")
		self.agent_count = tk.IntVar(value=60)
		self.count_input = ttk.Spinbox(side, from_=2, to=CELL_COUNT, textvariable=self.agent_count, width=10)
		self.count_input.pack(anchor="w", pady=(5, 14))

		controls = ttk.Frame(side)
		controls.pack(fill="x", pady=(0, 20))
		self.toggle_button = ttk.Button(controls, text="▶ Iniciar", command=self.toggle)
		self.toggle_button.pack(side="left")
		ttk.Button(controls, text="↺ Reiniciar", command=self.reset).pack(side="left", padx=(8, 0))

		self.round_label = self._stat(side, "RODADA", "0")
		self.population_label = self._stat(side, "AGENTES", "0")
		self.affinity_label = self._stat(side, "AFINIDADE LOCAL", "—")

		ttk.Separator(side).pack(fill="x", pady=16)
		ttk.Label(side, text="AGENTE SELECIONADO", foreground=MUTED, font=("DejaVu Sans", 9, "bold")).pack(anchor="w", pady=(0, 8))
		self.details = ttk.Frame(side)
		self.details.pack(fill="x")
		self.detail_labels = {}
		for label, key in (("Identificação", "id"), ("Sexo", "sexo"), ("Período", "período"), ("Curso", "curso"), ("Religião", "religião"), ("Origem", "origem")):
			row = ttk.Frame(self.details)
			row.pack(fill="x", pady=3)
			ttk.Label(row, text=label, foreground=MUTED).pack(side="left")
			value = ttk.Label(row, text="—", font=("DejaVu Sans", 9, "bold"), wraplength=145, justify="right")
			value.pack(side="right")
			self.detail_labels[key] = value

		ttk.Separator(side).pack(fill="x", pady=16)
		ttk.Label(side, text="PESOS DE SIMILARIDADE", foreground=MUTED, font=("DejaVu Sans", 9, "bold")).pack(anchor="w", pady=(0, 8))
		for trait, weight in (("Religião", "30%"), ("Origem", "30%"), ("Curso", "15%"), ("Período", "15%"), ("Sexo", "10%")):
			row = ttk.Frame(side)
			row.pack(fill="x", pady=2)
			ttk.Label(row, text=trait).pack(side="left")
			ttk.Label(row, text=weight, font=("DejaVu Sans", 9, "bold")).pack(side="right")

		self.status_label = ttk.Label(self.root, text="", style="Sub.TLabel", padding=(24, 0, 24, 8))
		self.status_label.pack(anchor="w")

	def _stat(self, parent, title, value):
		block = ttk.Frame(parent)
		block.pack(fill="x", pady=(0, 10))
		ttk.Label(block, text=title, foreground=MUTED, font=("DejaVu Sans", 8, "bold")).pack(anchor="w")
		label = ttk.Label(block, text=value, font=("DejaVu Sans", 17, "bold"))
		label.pack(anchor="w", pady=(2, 0))
		return label

	def reset(self):
		self.pause()
		try:
			count = max(2, min(CELL_COUNT, int(self.agent_count.get())))
		except (ValueError, tk.TclError):
			count = 60
		self.agent_count.set(count)
		cells = random.sample(range(CELL_COUNT), count)
		self.agents = [make_agent(index + 1) for index in range(count)]
		self.occupied = {}
		for agent, cell in zip(self.agents, cells):
			agent["x"], agent["y"] = cell % BOARD_SIZE, cell // BOARD_SIZE
			self.occupied[(agent["x"], agent["y"])] = agent
		self.round = 0
		self.selected_id = None
		self.last_move = None
		self._update_stats()
		self._show_agent(None)
		self.status_label.configure(text="Agentes distribuídos aleatoriamente. Selecione uma casa para inspecionar um perfil.")
		self.draw_board()

	def toggle(self):
		if self.running:
			self.pause()
		else:
			self.running = True
			self.toggle_button.configure(text="Ⅱ Pausar")
			self.status_label.configure(text="Simulação em andamento: cada rodada movimenta um agente.")
			self._step()

	def pause(self):
		self.running = False
		if hasattr(self, "toggle_button"):
			self.toggle_button.configure(text="▶ Iniciar")
		if self.after_id is not None:
			self.root.after_cancel(self.after_id)
			self.after_id = None

	def _step(self):
		if not self.running:
			return
		agent = random.choice(self.agents)
		targets = [other for other in self.agents if other is not agent]
		target = max(targets, key=lambda other: (similarity(agent, other), -self._distance(agent, other), random.random()))
		options = []
		for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
			new_x, new_y = agent["x"] + dx, agent["y"] + dy
			position = (new_x, new_y)
			if 0 <= new_x < BOARD_SIZE and 0 <= new_y < BOARD_SIZE and (position not in self.occupied or len(self.agents) == CELL_COUNT):
				options.append((self._distance_xy(new_x, new_y, target["x"], target["y"]), random.random(), new_x, new_y))
		self.round += 1
		self.selected_id = agent["id"]
		self.last_move = ((agent["x"], agent["y"]), None)
		if options:
			best_distance = min(option[0] for option in options)
			best_options = [option for option in options if option[0] == best_distance]
			_, _, new_x, new_y = random.choice(best_options)
			old_position = (agent["x"], agent["y"])
			displaced = self.occupied.get((new_x, new_y))
			del self.occupied[old_position]
			if displaced:
				displaced["x"], displaced["y"] = old_position
				self.occupied[old_position] = displaced
			agent["x"], agent["y"] = new_x, new_y
			self.occupied[(new_x, new_y)] = agent
			self.last_move = (old_position, (new_x, new_y))
		self._show_agent(agent)
		self._update_stats()
		self.draw_board()
		self.after_id = self.root.after(360, self._step)

	@staticmethod
	def _distance(first, second):
		return abs(first["x"] - second["x"]) + abs(first["y"] - second["y"])

	@staticmethod
	def _distance_xy(x1, y1, x2, y2):
		return abs(x1 - x2) + abs(y1 - y2)

	def _update_stats(self):
		self.round_label.configure(text=f"{self.round:,}")
		self.population_label.configure(text=f"{len(self.agents)} / {CELL_COUNT}")
		local_scores = []
		for agent in self.agents:
			neighbors = [other for other in self.agents if other is not agent and self._distance(agent, other) == 1]
			if neighbors:
				local_scores.append(sum(similarity(agent, other) for other in neighbors) / len(neighbors))
		average = sum(local_scores) / len(local_scores) if local_scores else None
		self.affinity_label.configure(text=f"{average:.0%}" if average is not None else "—")

	def _show_agent(self, agent):
		for key, label in self.detail_labels.items():
			value = agent[key] if agent else "—"
			if key == "período" and agent:
				value = f"{value}º período"
			label.configure(text=str(value))

	def _select_cell(self, event):
		cell_size = self._cell_size()
		x = int(event.x // cell_size)
		y = int(event.y // cell_size)
		if (x, y) in self.occupied:
			agent = self.occupied[(x, y)]
			self.selected_id = agent["id"]
			self._show_agent(agent)
			self.draw_board()

	def _cell_size(self):
		return min(self.canvas.winfo_width(), self.canvas.winfo_height()) / BOARD_SIZE

	def draw_board(self):
		if not hasattr(self, "canvas"):
			return
		self.canvas.delete("all")
		size = self._cell_size()
		for y in range(BOARD_SIZE):
			for x in range(BOARD_SIZE):
				left, top = x * size, y * size
				self.canvas.create_rectangle(left, top, left + size, top + size, fill="#f7f8f4", outline="#d6ddd5", width=1)
				agent = self.occupied.get((x, y))
				if agent:
					color = ATTRIBUTE_COLORS[RELIGIONS.index(agent["religião"])]
					inset = size * 0.16
					selected = agent["id"] == self.selected_id
					self.canvas.create_oval(left + inset, top + inset, left + size - inset, top + size - inset,
											fill=color, outline="#202927" if selected else "#ffffff", width=3 if selected else 1)
					if size >= 42:
						self.canvas.create_text(left + size / 2, top + size / 2, text=str(agent["id"]),
												fill="white", font=("DejaVu Sans", max(7, int(size * 0.17)), "bold"))
		if self.last_move and self.last_move[1]:
			(old_x, old_y), (new_x, new_y) = self.last_move
			self.canvas.create_line((old_x + 0.5) * size, (old_y + 0.5) * size,
									(new_x + 0.5) * size, (new_y + 0.5) * size,
									fill="#202927", width=2, arrow=tk.LAST, dash=(3, 2))


if __name__ == "__main__":
	application = tk.Tk()
	CultureSimulation(application)
	application.mainloop()
