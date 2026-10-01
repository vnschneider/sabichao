import { OpenAiLogo, TerminalWindow } from "@phosphor-icons/react";
import { APPS } from "../conteudo.js";
import "./Apps.css";

function Logo({ logo }) {
  if (logo === "openai") return <OpenAiLogo size={22} weight="fill" />;
  if (logo === "terminal") return <TerminalWindow size={22} weight="duotone" />;
  return <img src={logo} alt="" width="22" height="22" />;
}

export default function Apps() {
  return (
    <section className="secao apps">
      <div className="largura apps-grade">
        <div>
          <h2 className="secao-titulo">Use no app que voce ja tem</h2>
          <p className="secao-sub">
            Pergunte "quais sao minhas notas?" no seu assistente de IA. O instalador conecta o Sabichao
            aos apps que voce ja tem.
          </p>
        </div>
        <ul className="apps-lista" aria-label="Onde o Sabichao funciona">
          {APPS.map((app) => (
            <li key={app.nome}>
              <Logo logo={app.logo} />
              {app.nome}
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
