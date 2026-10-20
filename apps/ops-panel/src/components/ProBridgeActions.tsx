"use client";

import { useState } from "react";
import {
  buildProBridgePrompt,
  copyProBridgePrompt,
  openInClaudeAi,
  type ProBridgeSource,
} from "@/lib/proBridge";

type Props = {
  question: string;
  source: ProBridgeSource;
  agentId?: string;
  agent?: {
    name?: string;
    channel?: string;
    description?: string;
    area?: string;
  };
  history?: { role: "user" | "assistant"; content: string }[];
  /** Compact row for agent chat compose. */
  compact?: boolean;
};

export function ProBridgeActions({
  question,
  source,
  agentId,
  agent,
  history,
  compact,
}: Props) {
  const [status, setStatus] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  function prompt() {
    return buildProBridgePrompt({ question, history, agent });
  }

  async function onOpen() {
    if (busy) return;
    setBusy(true);
    setStatus(null);
    try {
      const { copied, opened } = await openInClaudeAi({
        prompt: prompt(),
        source,
        agentId,
      });
      if (copied && opened) {
        setStatus("Copied · Claude.ai opened — paste (⌘V / Ctrl+V). $0 API.");
      } else if (copied) {
        setStatus("Copied. Open claude.ai/new and paste. $0 API.");
      } else if (opened) {
        setStatus("Claude.ai opened — copy failed; use Copy prompt. $0 API.");
      } else {
        setStatus("Blocked popup/clipboard — use Copy prompt, then claude.ai/new.");
      }
    } finally {
      setBusy(false);
    }
  }

  async function onCopy() {
    if (busy) return;
    setBusy(true);
    setStatus(null);
    try {
      const ok = await copyProBridgePrompt({
        prompt: prompt(),
        source,
        agentId,
      });
      setStatus(
        ok
          ? "Prompt copied (safe SoT + question). Paste into Claude.ai Pro."
          : "Clipboard blocked — select text manually after opening Claude.ai.",
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <div
      className={compact ? "pro-bridge pro-bridge--compact" : "pro-bridge"}
      data-testid="pro-bridge"
    >
      {!compact ? (
        <p className="pro-bridge__lede">
          <strong>Pro bridge</strong> — Claude.ai Pro/Max is separate from the
          Anthropic API. Use your browser subscription ($0 API cost). Ops panel
          only builds a paste-ready prompt from safe SoT snippets.
        </p>
      ) : null}
      <div className="tools" style={{ marginBottom: compact ? 0 : 8 }}>
        <button
          type="button"
          className="btn primary"
          data-testid="pro-bridge-open"
          disabled={busy}
          onClick={() => void onOpen()}
        >
          Open in Claude.ai
        </button>
        <button
          type="button"
          className="btn ghost"
          data-testid="pro-bridge-copy"
          disabled={busy}
          onClick={() => void onCopy()}
        >
          Copy prompt
        </button>
      </div>
      {status ? (
        <p className="pro-bridge__status dim" data-testid="pro-bridge-status" role="status">
          {status}
        </p>
      ) : null}
    </div>
  );
}
