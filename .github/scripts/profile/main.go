// Genera las tarjetas de stats, lenguajes y la tabla de contribuciones
// recientes del README a partir de la API GraphQL de GitHub.
//
//	GITHUB_TOKEN=... go run ./.github/scripts/profile -user Crisiszzz07
package main

import (
	"bytes"
	"encoding/json"
	"flag"
	"fmt"
	"html"
	"log"
	"math"
	"net/http"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"time"
)

const query = `query($login:String!){
  user(login:$login){
    pullRequests{totalCount}
    merged: pullRequests(states:MERGED){totalCount}
    repositoriesContributedTo(contributionTypes:[COMMIT,PULL_REQUEST,PULL_REQUEST_REVIEW]){totalCount}
    contributionsCollection{
      totalCommitContributions
      contributionCalendar{ totalContributions weeks{ contributionDays{ contributionCount } } }
      commitContributionsByRepository(maxRepositories:25){
        repository{ ...repo }
        contributions(first:1, orderBy:{field:OCCURRED_AT, direction:DESC}){ totalCount nodes{ occurredAt } }
      }
      pullRequestContributions(first:50, orderBy:{direction:DESC}){
        nodes{ occurredAt pullRequest{ title url state repository{ ...repo } } }
      }
    }
    repositories(first:100, ownerAffiliations:OWNER, isFork:false){
      nodes{ languages(first:10, orderBy:{field:SIZE, direction:DESC}){ edges{ size node{ name color } } } }
    }
  }
}
fragment repo on Repository { nameWithOwner url isPrivate primaryLanguage{ name } }`

type repo struct {
	NameWithOwner   string `json:"nameWithOwner"`
	URL             string `json:"url"`
	IsPrivate       bool   `json:"isPrivate"`
	PrimaryLanguage *struct {
		Name string `json:"name"`
	} `json:"primaryLanguage"`
}

type count struct {
	TotalCount int `json:"totalCount"`
}

type user struct {
	PullRequests  count `json:"pullRequests"`
	Merged        count `json:"merged"`
	ContributedTo count `json:"repositoriesContributedTo"`
	Contributions struct {
		Commits  int `json:"totalCommitContributions"`
		Calendar struct {
			Total int `json:"totalContributions"`
			Weeks []struct {
				Days []struct {
					Count int `json:"contributionCount"`
				} `json:"contributionDays"`
			} `json:"weeks"`
		} `json:"contributionCalendar"`
		CommitsByRepo []struct {
			Repository    repo `json:"repository"`
			Contributions struct {
				TotalCount int `json:"totalCount"`
				Nodes      []struct {
					OccurredAt time.Time `json:"occurredAt"`
				} `json:"nodes"`
			} `json:"contributions"`
		} `json:"commitContributionsByRepository"`
		PRs struct {
			Nodes []struct {
				OccurredAt  time.Time `json:"occurredAt"`
				PullRequest struct {
					Title      string `json:"title"`
					URL        string `json:"url"`
					State      string `json:"state"`
					Repository repo   `json:"repository"`
				} `json:"pullRequest"`
			} `json:"nodes"`
		} `json:"pullRequestContributions"`
	} `json:"contributionsCollection"`
	Repositories struct {
		Nodes []struct {
			Languages struct {
				Edges []struct {
					Size int `json:"size"`
					Node struct {
						Name  string `json:"name"`
						Color string `json:"color"`
					} `json:"node"`
				} `json:"edges"`
			} `json:"languages"`
		} `json:"nodes"`
	} `json:"repositories"`
}

const font = `'JetBrains Mono','Fira Code',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace`

// Lenguajes de marcado/notebooks que inflan los bytes sin decir mucho.
var ignoredLangs = map[string]bool{"HTML": true, "CSS": true, "SCSS": true, "Jupyter Notebook": true, "Makefile": true}

// Textos de cada versión del README.
type locale struct {
	readme    string
	months    [12]string
	stats     [5]string
	weekly    string
	langTitle string
	langSub   string
	header    string
	footer    string
}

var locales = map[string]locale{
	"es": {
		readme:    "README.es.md",
		months:    [12]string{"ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"},
		stats:     [5]string{"contribuciones", "commits públicos", "pull requests", "PRs merged", "repos externos"},
		weekly:    "contribuciones por semana · últimos 12 meses",
		langTitle: "LENGUAJES",
		langSub:   "por bytes · repos propios",
		header:    "| # | repo | lo último | commits | fecha |",
		footer:    "Últimos 12 meses · actualizado el %s",
	},
	"en": {
		readme:    "README.md",
		months:    [12]string{"jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"},
		stats:     [5]string{"contributions", "public commits", "pull requests", "merged PRs", "external repos"},
		weekly:    "contributions per week · last 12 months",
		langTitle: "LANGUAGES",
		langSub:   "by bytes · own repos",
		header:    "| # | repo | latest | commits | date |",
		footer:    "Last 12 months · updated %s",
	},
}

func main() {
	login := flag.String("user", os.Getenv("GITHUB_REPOSITORY_OWNER"), "usuario de GitHub")
	out := flag.String("out", "assets/generated", "carpeta de salida de los SVG")
	limit := flag.Int("limit", 8, "número de repos recientes")
	flag.Parse()

	token := os.Getenv("GITHUB_TOKEN")
	u, err := fetch(*login, token)
	if err != nil {
		log.Fatal(err)
	}
	if err := os.MkdirAll(*out, 0o755); err != nil {
		log.Fatal(err)
	}
	recent := recentActivity(u, *login, token, *limit)
	for code, l := range locales {
		write(filepath.Join(*out, "stats."+code+".svg"), statsSVG(u, l))
		write(filepath.Join(*out, "languages."+code+".svg"), languagesSVG(u, l))

		b, err := os.ReadFile(l.readme)
		if err != nil {
			log.Fatal(err)
		}
		updated, err := replaceBetween(string(b), "<!--recent:start-->", "<!--recent:end-->", recentTable(recent, *login, l))
		if err != nil {
			log.Fatal(err)
		}
		write(l.readme, updated)
	}
}

func fetch(login, token string) (*user, error) {
	if token == "" {
		return nil, fmt.Errorf("falta GITHUB_TOKEN")
	}
	body, _ := json.Marshal(map[string]any{"query": query, "variables": map[string]string{"login": login}})
	req, _ := http.NewRequest("POST", "https://api.github.com/graphql", bytes.NewReader(body))
	req.Header.Set("Authorization", "bearer "+token)
	res, err := http.DefaultClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer res.Body.Close()
	var r struct {
		Data struct {
			User *user `json:"user"`
		} `json:"data"`
		Errors []struct {
			Message string `json:"message"`
		} `json:"errors"`
	}
	if err := json.NewDecoder(res.Body).Decode(&r); err != nil {
		return nil, err
	}
	if len(r.Errors) > 0 {
		return nil, fmt.Errorf("graphql: %s", r.Errors[0].Message)
	}
	if r.Data.User == nil {
		return nil, fmt.Errorf("usuario %q no encontrado", login)
	}
	return r.Data.User, nil
}

func write(path, s string) {
	if err := os.WriteFile(path, []byte(s), 0o644); err != nil {
		log.Fatal(err)
	}
}

func replaceBetween(s, start, end, content string) (string, error) {
	i, j := strings.Index(s, start), strings.Index(s, end)
	if i < 0 || j < i {
		return "", fmt.Errorf("no encontré los marcadores %s … %s", start, end)
	}
	return s[:i+len(start)] + "\n" + content + "\n" + s[j:], nil
}

// ---------- tabla de contribuciones recientes ----------

type activity struct {
	repo      repo
	last      time.Time
	commits   int
	prTitle   string
	prURL     string
	prState   string
	commitMsg string
	commitURL string
}

// recentActivity junta commits y PRs por repo y devuelve los más recientes.
func recentActivity(u *user, login, token string, limit int) []*activity {
	byRepo := map[string]*activity{}
	get := func(r repo) *activity {
		a, ok := byRepo[r.NameWithOwner]
		if !ok {
			a = &activity{repo: r}
			byRepo[r.NameWithOwner] = a
		}
		return a
	}
	for _, c := range u.Contributions.CommitsByRepo {
		a := get(c.Repository)
		a.commits = c.Contributions.TotalCount
		if n := c.Contributions.Nodes; len(n) > 0 && n[0].OccurredAt.After(a.last) {
			a.last = n[0].OccurredAt
		}
	}
	for _, p := range u.Contributions.PRs.Nodes { // ya vienen del más reciente al más antiguo
		a := get(p.PullRequest.Repository)
		// el PR más reciente, salvo que haya uno merged: ese tiene prioridad
		if a.prURL == "" || (a.prState != "MERGED" && p.PullRequest.State == "MERGED") {
			a.prTitle, a.prURL, a.prState = p.PullRequest.Title, p.PullRequest.URL, p.PullRequest.State
		}
		if p.OccurredAt.After(a.last) {
			a.last = p.OccurredAt
		}
	}

	var list []*activity
	for name, a := range byRepo {
		if a.repo.IsPrivate || strings.EqualFold(name, login+"/"+login) {
			continue
		}
		list = append(list, a)
	}
	sort.Slice(list, func(i, j int) bool { return list[i].last.After(list[j].last) })
	if len(list) > limit {
		list = list[:limit]
	}
	for _, a := range list {
		if a.prURL == "" {
			a.commitMsg, a.commitURL = lastCommit(a.repo.NameWithOwner, login, token)
		}
	}
	return list
}

func recentTable(list []*activity, login string, l locale) string {
	var b strings.Builder
	b.WriteString(l.header + "\n|:-:|---|---|:-:|--:|\n")
	for i, a := range list {
		name := a.repo.NameWithOwner
		if owner, short, _ := strings.Cut(name, "/"); strings.EqualFold(owner, login) {
			name = short
		}
		lang := ""
		if a.repo.PrimaryLanguage != nil {
			lang = " <sub>" + a.repo.PrimaryLanguage.Name + "</sub>"
		}
		what := "—"
		if a.prURL != "" {
			what = fmt.Sprintf("%s [%s](%s)", badge("PR", strings.ToLower(a.prState)), mdEscape(a.prTitle), a.prURL)
		} else if a.commitURL != "" {
			what = fmt.Sprintf("%s [%s](%s)", badge("commit", ""), mdEscape(a.commitMsg), a.commitURL)
		}
		commits := "—"
		if a.commits > 0 {
			commits = fmt.Sprint(a.commits)
		}
		fmt.Fprintf(&b, "| `%02d` | [**%s**](%s)%s | %s | %s | %s |\n",
			i+1, name, a.repo.URL, lang, what, commits, shortDate(a.last, l.months))
	}
	fmt.Fprintf(&b, "\n<sub>"+l.footer+"</sub>", time.Now().UTC().Format("2006-01-02"))
	return b.String()
}

func badge(label, state string) string {
	color := map[string]string{"merged": "8957e5", "open": "238636", "closed": "6e7681", "": "5a189a"}[state]
	msg := state
	if msg == "" {
		msg, label = label, ""
	}
	return fmt.Sprintf(`<img src="https://img.shields.io/badge/%s-%s-%s?style=flat-square&labelColor=240046" alt="%s" align="absmiddle"/>`, label, msg, color, msg)
}

// lastCommit devuelve el primer renglón y el enlace del último commit
// del usuario en la rama por defecto del repo.
func lastCommit(nwo, login, token string) (msg, url string) {
	req, _ := http.NewRequest("GET", "https://api.github.com/repos/"+nwo+"/commits?per_page=1&author="+login, nil)
	req.Header.Set("Authorization", "bearer "+token)
	res, err := http.DefaultClient.Do(req)
	if err != nil {
		return "", ""
	}
	defer res.Body.Close()
	var commits []struct {
		HTMLURL string `json:"html_url"`
		Commit  struct {
			Message string `json:"message"`
		} `json:"commit"`
	}
	if json.NewDecoder(res.Body).Decode(&commits) != nil || len(commits) == 0 {
		return "", ""
	}
	msg, _, _ = strings.Cut(commits[0].Commit.Message, "\n")
	if r := []rune(msg); len(r) > 72 {
		msg = string(r[:71]) + "…"
	}
	return msg, commits[0].HTMLURL
}

func shortDate(t time.Time, months [12]string) string {
	t = t.Local()
	if t.Year() == time.Now().Year() {
		return fmt.Sprintf("%d %s", t.Day(), months[t.Month()-1])
	}
	return fmt.Sprintf("%d %s %d", t.Day(), months[t.Month()-1], t.Year()%100)
}

func mdEscape(s string) string {
	return strings.NewReplacer("|", `\|`, "[", `\[`, "]", `\]`, "<", "&lt;").Replace(s)
}

// ---------- stats.svg ----------

func statsSVG(u *user, l locale) string {
	c := u.Contributions
	stats := []struct {
		n     int
		label string
	}{
		{c.Calendar.Total, l.stats[0]},
		{c.Commits, l.stats[1]},
		{u.PullRequests.TotalCount, l.stats[2]},
		{u.Merged.TotalCount, l.stats[3]},
		{u.ContributedTo.TotalCount, l.stats[4]},
	}

	var weeks []int
	peak := 1
	for _, w := range c.Calendar.Weeks {
		n := 0
		for _, d := range w.Days {
			n += d.Count
		}
		weeks = append(weeks, n)
		peak = max(peak, n)
	}

	var s strings.Builder
	fmt.Fprintf(&s, `<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="250" viewBox="0 0 1000 250" font-family="%s">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0d0221"/><stop offset="1" stop-color="#240046"/></linearGradient>
  <linearGradient id="bar" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#5a189a"/><stop offset=".7" stop-color="#c77dff"/><stop offset="1" stop-color="#ff6ec7"/></linearGradient>
</defs>
<style>
  .b{animation:up .9s cubic-bezier(.2,.8,.2,1) both;transform-box:fill-box;transform-origin:50%% 100%%}
  @keyframes up{from{transform:scaleY(0)}}
  .n{animation:fade .6s ease-out both}
  @keyframes fade{from{opacity:0;transform:translateY(6px)}}
</style>
<rect width="1000" height="250" rx="16" fill="url(#bg)"/>
<rect x=".5" y=".5" width="999" height="249" rx="16" fill="none" stroke="#5a189a" stroke-opacity=".7"/>
`, font)
	colW := 920.0 / float64(len(stats))
	for i, st := range stats {
		x := 40 + colW*float64(i) + colW/2
		fmt.Fprintf(&s, `<g class="n" style="animation-delay:%.2fs"><text x="%.0f" y="62" text-anchor="middle" font-size="34" font-weight="800" fill="#f3e8ff">%d</text><text x="%.0f" y="86" text-anchor="middle" font-size="12" fill="#c77dff" letter-spacing="1">%s</text></g>`+"\n",
			float64(i)*0.08, x, st.n, x, html.EscapeString(st.label))
		if i > 0 {
			fmt.Fprintf(&s, `<line x1="%.0f" y1="36" x2="%.0f" y2="92" stroke="#3c096c"/>`+"\n", 40+colW*float64(i), 40+colW*float64(i))
		}
	}

	// forma de onda: una barra por semana
	const top, bottom = 120.0, 212.0
	bw := 920.0 / float64(max(len(weeks), 1))
	fmt.Fprintf(&s, `<line x1="40" y1="%.0f" x2="960" y2="%.0f" stroke="#3c096c"/>`+"\n", bottom+.5, bottom+.5)
	for i, n := range weeks {
		h := math.Max(2, (bottom-top)*math.Sqrt(float64(n)/float64(peak)))
		fmt.Fprintf(&s, `<rect class="b" x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="2" fill="url(#bar)" opacity="%.2f" style="animation-delay:%.2fs"><title>%d</title></rect>`+"\n",
			40+bw*float64(i)+1.5, bottom-h, bw-3, h, 0.35+0.65*float64(n)/float64(peak), 0.3+float64(i)*0.015, n)
	}
	fmt.Fprintf(&s, `<text x="40" y="236" font-size="11" fill="#9d8bb0">%s</text>
</svg>`, l.weekly)
	return s.String()
}

// ---------- languages.svg ----------

func languagesSVG(u *user, loc locale) string {
	type lang struct {
		name, color string
		size        int
	}
	sizes := map[string]*lang{}
	total := 0
	for _, r := range u.Repositories.Nodes {
		for _, e := range r.Languages.Edges {
			if ignoredLangs[e.Node.Name] {
				continue
			}
			l, ok := sizes[e.Node.Name]
			if !ok {
				l = &lang{name: e.Node.Name, color: e.Node.Color}
				sizes[e.Node.Name] = l
			}
			l.size += e.Size
			total += e.Size
		}
	}
	var langs []*lang
	for _, l := range sizes {
		langs = append(langs, l)
	}
	sort.Slice(langs, func(i, j int) bool { return langs[i].size > langs[j].size })
	if len(langs) > 6 {
		langs = langs[:6]
	}
	total = max(total, 1)

	var s strings.Builder
	fmt.Fprintf(&s, `<svg xmlns="http://www.w3.org/2000/svg" width="495" height="195" viewBox="0 0 495 195" font-family="%s">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0d0221"/><stop offset="1" stop-color="#240046"/></linearGradient>
  <linearGradient id="bar" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#7b2cbf"/><stop offset="1" stop-color="#ff6ec7"/></linearGradient>
</defs>
<style>
  .b{animation:grow 1s cubic-bezier(.2,.8,.2,1) both;transform-box:fill-box;transform-origin:0 50%%}
  @keyframes grow{from{transform:scaleX(0)}}
</style>
<rect width="495" height="195" rx="12" fill="url(#bg)"/>
<rect x=".5" y=".5" width="494" height="194" rx="12" fill="none" stroke="#5a189a"/>
<text x="24" y="34" font-size="14" font-weight="700" fill="#c77dff" letter-spacing="1">%s</text>
<text x="471" y="34" text-anchor="end" font-size="10" fill="#7b6a8f">%s</text>
`, font, loc.langTitle, loc.langSub)
	for i, l := range langs {
		y := 58 + i*22
		pct := float64(l.size) / float64(total)
		color := l.color
		if color == "" {
			color = "#c77dff"
		}
		fmt.Fprintf(&s, `<circle cx="28" cy="%d" r="4" fill="%s"/><text x="40" y="%d" font-size="12" fill="#f3e8ff">%s</text>
<rect x="150" y="%d" width="260" height="8" rx="4" fill="#2a1446"/><rect class="b" x="150" y="%d" width="%.1f" height="8" rx="4" fill="url(#bar)" style="animation-delay:%.2fs"/>
<text x="471" y="%d" text-anchor="end" font-size="11" fill="#e0aaff">%.1f%%</text>
`, y-4, color, y, html.EscapeString(l.name), y-11, y-11, math.Max(4, 260*pct), float64(i)*0.1, y, pct*100)
	}
	s.WriteString("</svg>")
	return s.String()
}
