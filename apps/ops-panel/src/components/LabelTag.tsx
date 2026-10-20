import type { ConfidenceLabel } from "@/lib/ops-data";

export function LabelTag({ label }: { label: ConfidenceLabel }) {
  return <span className={`label-tag ${label}`}>{label}</span>;
}
