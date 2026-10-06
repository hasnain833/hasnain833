"""Write README.md from the section data, so links and alt text never drift.

Every graphic is a <picture> with a dark and a light version; GitHub serves the
one that matches the visitor's theme.

Usage: python scripts/build_readme.py
"""
from make_sections import CONTACT, HISTORY, PROJECTS, STACK


def pic(name: str, alt: str, width: str) -> str:
    return (f'<picture><source media="(prefers-color-scheme: dark)" srcset="./{name}-dark.svg">'
            f'<img src="./{name}-light.svg" width="{width}" alt="{alt}"></picture>')


def prompt(cmd: str) -> str:
    return f"<h3><code>hasnain@github ~ $ {cmd}</code></h3>"


def main():
    p = []
    p.append('<div align="center">\n')
    p.append(pic("assets/city", "Hasnain Aftab — GitHub contributions over the last year as an animated isometric city", "100%"))
    p.append('\n\n<b>Full stack engineer</b> building production web apps with Next.js and Node.js, '
             'and wiring LLMs into them — Claude, OpenAI, LangChain and RAG.<br>'
             'Full Stack Web Developer at BitzSol, Islamabad · freelancing for clients in 3 countries.\n')
    p.append("</div>\n\n<br>\n")

    p.append(prompt("whoami") + "\n")
    p.append('<p align="center">'
             + pic("assets/portrait", "ASCII portrait of Hasnain Aftab", "42.5%") + "\n"
             + pic("assets/card", "Neofetch-style card: Full Stack Engineer at BitzSol, AI integration, "
                   "freelance for clients in 3 countries, 10+ production apps", "56.5%")
             + "</p>\n\n")

    p.append(prompt("./contact.sh") + "\n<p align=\"center\">\n")
    for label, value, url, _ in CONTACT:
        p.append(f'<a href="{url}">' + pic(f"assets/contact-{label}", f"{label}: {value}", "24%") + "</a>\n")
    p.append("</p>\n\n<br>\n\n")

    p.append(prompt("ls ./projects") + "\n<p align=\"center\">\n")
    for slug, title, stack, desc, url, _, _ in PROJECTS:
        p.append(f'<a href="{url}">' + pic(f"assets/project-{slug}", f"{title}: {desc}. Built with {stack}.", "49%")
                 + "</a>\n")
    p.append("</p>\n\n<br>\n\n")

    p.append(prompt("cat stack.txt") + "\n<p align=\"center\">"
             + pic("assets/stack", "Tech stack — " + "; ".join(f"{n}: {', '.join(i)}" for n, i, _ in STACK), "100%")
             + "</p>\n\n<br>\n\n")

    p.append(prompt("history") + "\n<p align=\"center\">"
             + pic("assets/history", "Career — " + "; ".join(f"{pl} ({r}), {y}" for y, m, pl, r, _ in HISTORY), "100%")
             + "</p>\n\n")

    p.append("<details>\n<summary><b>Certifications and languages</b></summary>\n<br>\n\n"
             "**Certifications:** React.js (Udemy) · JavaScript Algorithms and Data Structures (freeCodeCamp) · "
             "MERN Stack Development (Coursera)<br>\n"
             "**Languages:** English · Urdu · Punjabi\n\n</details>\n\n<br>\n\n")

    p.append('<div align="center">\n\n<code>hasnain@github ~ $ exit</code><br>\n'
             "<sub>Open to onsite roles in Islamabad, Rawalpindi, Lahore and Karachi · "
             '<a href="mailto:contact@has-nain.dev">contact@has-nain.dev</a> · '
             "the city above rebuilds itself every day from my real contributions</sub>\n\n</div>\n")

    open("README.md", "w", encoding="utf-8").write("".join(p))
    print("wrote README.md")


if __name__ == "__main__":
    main()
