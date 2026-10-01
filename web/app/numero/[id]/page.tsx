import { notFound } from "next/navigation";
import { Issue } from "@/components/Issue";
import { allEpisodes, getEpisode } from "@/lib/episodes";

export const dynamicParams = false;
export const generateStaticParams = () => allEpisodes().map((e) => ({ id: e.id }));

export default async function IssuePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const ep = getEpisode(id);
  if (!ep) notFound();
  return <Issue ep={ep} />;
}
