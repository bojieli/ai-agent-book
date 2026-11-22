import { layoutAsyncArchitecture } from './async-architecture-layout.mjs';
import { layoutVoiceArchitecture } from './voice-architecture-layout.mjs';
import { layoutComputerUse } from './computer-use-layout.mjs';
import { layoutMemoryFoundation } from './memory-foundation-layout.mjs';
import { layoutRetrievalStructure } from './retrieval-structure-layout.mjs';
import { layoutRetrievalWorkflow } from './retrieval-workflow-layout.mjs';
import { layoutTrajectory } from './trajectory-figure.mjs';
import { layoutContextFlow } from './context-flow-figures.mjs';
import { availableChapters } from '../src/lib/available-chapters.mjs';
import editions from '../src/lib/editions.json' with { type: 'json' };
import { layoutToolProtocol } from './tool-protocol-layout.mjs';
import { layoutToolCache } from './tool-cache-layout.mjs';
import { layoutCodingCore } from './coding-core-layout.mjs';
import { layoutCodingComparison } from './coding-comparison-layout.mjs';
import { layoutCodingProduction } from './coding-production-layout.mjs';
import { layoutCodingApplication } from './coding-application-layout.mjs';
import { layoutContextWindow } from './context-window-figure.mjs';
import { layoutAgentLoop } from './agent-loop-figure.mjs';
import { layoutEvaluationEnvironments } from './evaluation-environments-figure.mjs';
import { layoutLlmJudge } from './llm-judge-figure.mjs';
import { layoutObservability } from './observability-figure.mjs';
import {
  layoutVerificationSpectrum,
  layoutSimulationFidelity,
} from './evaluation-spectrum-figures.mjs';
import {
  layoutEvaluationOverview,
  layoutDualControl,
  layoutEmbodiedEvaluation,
} from './evaluation-overview-figures.mjs';
import { layoutPairwise } from './pairwise-figure.mjs';
import { layoutImprovementCycle } from './improvement-cycle-figure.mjs';
import { layoutGridWorld } from './grid-world-figure.mjs';
import { layoutGrpoRollouts } from './grpo-rollouts-figure.mjs';
import {
  layoutMdp,
  layoutRlInteraction,
  layoutNextToken,
  layoutSftToRl,
  layoutQUpdate,
  layoutTrainingAgents,
  layoutVlmTraining,
} from './training-foundations-figures.mjs';
import {
  layoutSftPipeline,
  layoutToolRl,
} from './training-workflows-figures.mjs';
import { styleFigure, frameRaster } from './figure-style.mjs';
import {
  layoutTurnComparison,
  layoutCreditAssignment,
} from './training-sequences-figures.mjs';
import {
  layoutReTool,
  layoutTrainingSystem,
} from './training-systems-figures.mjs';
import { figurePaths } from '../src/lib/figure-paths.mjs';
import {
  layoutEvolutionLoop,
  layoutExperienceKnowledge,
  layoutEvolutionDeployment,
} from './evolution-flow-figures.mjs';
import {
  layoutTrajectoryVerification,
  layoutEvolutionMethods,
} from './evolution-methods-figures.mjs';
import {
  layoutSharedContextComparison,
  layoutVirtualFilesystemMounts,
  layoutProposerReviewerLoop,
  layoutManagerSequentialCoordination,
} from './collaboration-context-figures.mjs';
import {
  layoutBookTranslationManager,
  layoutManagerParallelCoordination,
  layoutPhoneComputerCollaboration,
  layoutCascadingTermination,
} from './collaboration-manager-figures.mjs';
import {
  layoutMetaGPTCollaboration,
  layoutAITownArchitecture,
  layoutVoiceWerewolfSystem,
} from './collaboration-society-figures.mjs';
import { readFile, mkdir, copyFile, writeFile } from 'node:fs/promises';
const root = new URL('../../', import.meta.url);
let count = 0;
for (const [locale, { directory, suffix }] of Object.entries(editions)) {
  for (const chapterNumber of availableChapters) {
    const markdown = await readFile(
      new URL(`${directory}/chapter${chapterNumber}${suffix}.md`, root),
      'utf8',
    );
    const images = new Set(
      [...markdown.matchAll(/!\[[^\]]*\]\((images\/[^)]+)\)/g)].map(
        (match) => match[1],
      ),
    );
    for (const image of images) {
      const destination = new URL(
        `../public/${directory}/${image}`,
        import.meta.url,
      );
      await mkdir(new URL('./', destination), { recursive: true });
      const original = new URL(`${directory}/${image}`, root);
      // The original URL always serves the untouched source file.
      await copyFile(original, destination);
      const bytes = await readFile(original);
      let vector;
      const englishReplacement =
        directory === 'book-en' &&
        /^images\/fig2-(7|9|10|12|13|14|15|16|17)\.(svg|png)$/.exec(image);
      if (englishReplacement) {
        vector = await readFile(
          new URL(
            `../public/figures/chapter2-en/fig2-${englishReplacement[1]}-web.svg`,
            import.meta.url,
          ),
          'utf8',
        );
      } else if (image === 'images/fig1-1.svg')
        vector = layoutAgentLoop(bytes.toString());
      else if (image === 'images/fig1-4.svg')
        vector = layoutTrajectory(bytes.toString(), {
          rtl: ['book-ar', 'book-he'].includes(directory),
        });
      else if (image === 'images/fig2-1.svg')
        vector = layoutContextWindow(bytes.toString());
      else if (/^images\/fig2-(2|3|4|5|8|11)\.svg$/.test(image))
        vector = layoutContextFlow(
          bytes.toString(),
          Number(image.match(/fig2-(\d+)/)[1]),
          { rtl: ['book-ar', 'book-he'].includes(directory) },
        );
      else if (/^images\/fig3-(1|3|4|5|7)\.svg$/.test(image))
        vector = layoutMemoryFoundation(
          bytes.toString(),
          Number(image.match(/fig3-(\d+)/)[1]),
          { rtl: ['book-ar', 'book-he'].includes(directory) },
        );
      else if (/^images\/fig3-(9|10|11|12)\.svg$/.test(image))
        vector = layoutRetrievalStructure(
          bytes.toString(),
          Number(image.match(/fig3-(\d+)/)[1]),
          { rtl: ['book-ar', 'book-he'].includes(directory) },
        );
      else if (/^images\/fig3-(13|14|15)\.svg$/.test(image))
        vector = layoutRetrievalWorkflow(
          bytes.toString(),
          Number(image.match(/fig3-(\d+)/)[1]),
          { rtl: ['book-ar', 'book-he'].includes(directory) },
        );
      else if (/^images\/fig4-(1|2)\.svg$/.test(image))
        vector = layoutToolProtocol(
          bytes.toString(),
          Number(image.match(/fig4-(\d+)/)[1]),
          {
            rtl: ['book-ar', 'book-he'].includes(directory),
          },
        );
      else if (/^images\/fig4-(3|4)\.svg$/.test(image))
        vector = layoutToolCache(
          bytes.toString(),
          Number(image.match(/fig4-(\d+)/)[1]),
          {
            rtl: ['book-ar', 'book-he'].includes(directory),
          },
        );
      else if (/^images\/fig5-(1|2)\.svg$/.test(image))
        vector = layoutCodingCore(
          bytes.toString(),
          Number(image.match(/fig5-(\d+)/)[1]),
          { rtl: ['book-ar', 'book-he'].includes(directory) },
        );
      else if (/^images\/fig5-(3|4)\.svg$/.test(image))
        vector = layoutCodingComparison(
          bytes.toString(),
          Number(image.match(/fig5-(\d+)/)[1]),
          { rtl: ['book-ar', 'book-he'].includes(directory) },
        );
      else if (/^images\/fig5-(5|6|7)\.svg$/.test(image))
        vector = layoutCodingProduction(
          bytes.toString(),
          Number(image.match(/fig5-(\d+)/)[1]),
          { rtl: ['book-ar', 'book-he'].includes(directory) },
        );
      else if (/^images\/fig5-(8|9|10|11)\.svg$/.test(image))
        vector = layoutCodingApplication(
          bytes.toString(),
          Number(image.match(/fig5-(\d+)/)[1]),
          { rtl: ['book-ar', 'book-he'].includes(directory) },
        );
      else if (/^images\/fig6-([1-5])\.svg$/.test(image))
        vector = layoutAsyncArchitecture(
          bytes.toString(),
          Number(image.match(/fig6-(\d+)/)[1]),
          { rtl: ['book-ar', 'book-he'].includes(directory) },
        );
      else if (/^images\/fig6-(6|7|8|9|10)\.svg$/.test(image))
        vector = layoutVoiceArchitecture(
          bytes.toString(),
          Number(image.match(/fig6-(\d+)/)[1]),
          { rtl: ['book-ar', 'book-he'].includes(directory) },
        );
      else if (/^images\/fig6-(11|12|13|14)\.svg$/.test(image))
        vector = layoutComputerUse(
          bytes.toString(),
          Number(image.match(/fig6-(\d+)/)[1]),
          { rtl: ['book-ar', 'book-he'].includes(directory) },
        );
      else if (image === 'images/fig7-2.svg')
        vector = layoutEvaluationEnvironments(bytes.toString(), {
          rtl: ['book-ar', 'book-he'].includes(directory),
        });
      else if (image === 'images/fig7-5.svg')
        vector = layoutLlmJudge(bytes.toString(), {
          rtl: ['book-ar', 'book-he'].includes(directory),
        });
      else if (image === 'images/fig7-7.svg')
        vector = layoutObservability(bytes.toString(), {
          rtl: ['book-ar', 'book-he'].includes(directory),
        });
      else if (image === 'images/fig7-4.svg')
        vector = layoutVerificationSpectrum(bytes.toString(), {
          rtl: ['book-ar', 'book-he'].includes(directory),
        });
      else if (image === 'images/fig7-9.svg')
        vector = layoutSimulationFidelity(bytes.toString(), {
          rtl: ['book-ar', 'book-he'].includes(directory),
        });
      else if (image === 'images/fig7-1.svg')
        vector = layoutEvaluationOverview(bytes.toString(), {
          rtl: ['book-ar', 'book-he'].includes(directory),
        });
      else if (image === 'images/fig7-3.svg')
        vector = layoutDualControl(bytes.toString(), {
          rtl: ['book-ar', 'book-he'].includes(directory),
        });
      else if (image === 'images/fig7-6.svg')
        vector = layoutPairwise(bytes.toString(), {
          rtl: ['book-ar', 'book-he'].includes(directory),
        });
      else if (image === 'images/fig7-8.svg')
        vector = layoutImprovementCycle(bytes.toString(), {
          rtl: ['book-ar', 'book-he'].includes(directory),
        });
      else if (image === 'images/fig7-10.svg')
        vector = layoutEmbodiedEvaluation(bytes.toString(), {
          rtl: ['book-ar', 'book-he'].includes(directory),
        });
      else if (image === 'images/fig8-1.svg')
        vector = layoutRlInteraction(bytes.toString());
      else if (image === 'images/fig8-2.svg')
        vector = layoutMdp(bytes.toString());
      else if (image === 'images/fig8-3.svg')
        vector = layoutGridWorld(bytes.toString());
      else if (image === 'images/fig8-10.svg')
        vector = layoutSftPipeline(bytes.toString());
      else if (image === 'images/fig8-11.svg')
        vector = layoutSftToRl(bytes.toString(), { english: locale === 'en' });
      else if (image === 'images/fig8-16.svg')
        vector = layoutToolRl(bytes.toString());
      else if (image === 'images/fig8-4.svg')
        vector = layoutQUpdate(bytes.toString());
      else if (image === 'images/fig8-7.svg')
        vector = layoutTrainingAgents(bytes.toString());
      else if (image === 'images/fig8-8.svg')
        vector = layoutNextToken(bytes.toString(), {
          chineseExampleSource:
            locale === 'en'
              ? await readFile(new URL('book/images/fig8-8.svg', root), 'utf8')
              : undefined,
        });
      else if (image === 'images/fig8-9.svg')
        vector = layoutVlmTraining(bytes.toString());
      else if (image === 'images/fig8-13.svg')
        vector = layoutGrpoRollouts(locale);
      else if (image === 'images/fig8-14.svg')
        vector = layoutTurnComparison(bytes.toString());
      else if (image === 'images/fig8-15.svg')
        vector = layoutCreditAssignment(bytes.toString());
      else if (image === 'images/fig8-17.svg')
        vector = layoutReTool(bytes.toString());
      else if (image === 'images/fig8-18.svg')
        vector = layoutTrainingSystem(bytes.toString());
      else if (image === 'images/fig9-1.svg')
        vector = layoutEvolutionLoop(bytes.toString());
      else if (image === 'images/fig9-2.svg')
        vector = layoutTrajectoryVerification(bytes.toString());
      else if (image === 'images/fig9-3.svg')
        vector = layoutEvolutionMethods(bytes.toString());
      else if (image === 'images/fig9-4.svg')
        vector = layoutExperienceKnowledge(bytes.toString());
      else if (image === 'images/fig9-5.svg')
        vector = layoutEvolutionDeployment(bytes.toString());
      else if (image === 'images/fig10-1.svg')
        vector = layoutSharedContextComparison(bytes.toString());
      else if (image === 'images/fig10-2.svg')
        vector = layoutVirtualFilesystemMounts(bytes.toString());
      else if (image === 'images/fig10-3.svg')
        vector = layoutProposerReviewerLoop(bytes.toString());
      else if (image === 'images/fig10-4.svg')
        vector = layoutManagerSequentialCoordination(bytes.toString());
      else if (image === 'images/fig10-5.svg')
        vector = layoutBookTranslationManager(bytes.toString());
      else if (image === 'images/fig10-6.svg')
        vector = layoutManagerParallelCoordination(bytes.toString());
      else if (image === 'images/fig10-7.svg')
        vector = layoutPhoneComputerCollaboration(bytes.toString());
      else if (image === 'images/fig10-8.svg')
        vector = layoutCascadingTermination(bytes.toString());
      else if (image === 'images/fig10-9.svg')
        vector = layoutMetaGPTCollaboration(bytes.toString());
      else if (image === 'images/fig10-10.svg')
        vector = layoutAITownArchitecture(bytes.toString());
      else if (image === 'images/fig10-11.svg')
        vector = layoutVoiceWerewolfSystem(bytes.toString());
      else if (image.endsWith('.svg')) vector = bytes.toString();
      const paths = figurePaths(directory, image);
      for (const theme of ['light', 'dark']) {
        const target = new URL(`../public${paths[theme]}`, import.meta.url);
        await mkdir(new URL('./', target), { recursive: true });
        // Chapter 1/2 raster figures are PNGs; read dimensions from their IHDR.
        if (
          !vector &&
          !bytes
            .subarray(0, 8)
            .equals(Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]))
        )
          throw new Error(`Unsupported raster figure: ${image}`);
        await writeFile(
          target,
          vector
            ? styleFigure(vector, theme, {
                preserveHeatmap: image === 'images/fig2-6.svg',
              })
            : frameRaster(
                bytes,
                'image/png',
                bytes.readUInt32BE(16),
                bytes.readUInt32BE(20),
                theme,
              ),
        );
      }
      count++;
    }
  }
}
console.log(`Prepared ${count} chapter figures from the original sources.`);
