import { ref } from "vue";

import { useApi } from "@/services/backend/client";
import type { AppConfig } from "@/types/mediamanager/app";
import type { GenericCollection } from "@/types/non_generated/api";
import type { TautulliLibrary } from "@/types/mediamanager/expired-media";

export const useAppConfig = function () {
    const api = useApi();
    const appConfig = ref<AppConfig>();
    const allLibraryChoices = ref<TautulliLibrary[]>([]);
    const selectedLibraryChoices = ref<string[]>();

    const actions = {
        async refresh() {
            async function refreshAppConfig() {
                const { data } = await api.get<AppConfig>("/api/config")
                appConfig.value = data || undefined;
            }

            async function refreshLibraryChoices() {
                const { data } = await api.get<GenericCollection<TautulliLibrary>>("/api/manage-media/libraries");
                if (!data) {
                    return;
                }

                allLibraryChoices.value = data.items.filter((choice) => choice.sectionType !== "unknown" && choice.isActive).sort(
                    (a, b) => {
                        return a.sectionName > b.sectionName ? 1 : -1;
                    }
                );
            }

            await Promise.all([
                refreshAppConfig(),
                refreshLibraryChoices(),
            ]);

            if (!(appConfig.value?.monitoredLibraryIds?.length && allLibraryChoices.value?.length)) {
                return;
            }

            // populate selected choices
            const choices: string[] = [];
            allLibraryChoices.value.forEach((choice) => {
                if (appConfig.value?.monitoredLibraryIds?.includes(choice.sectionId)) {
                    choices.push(choice.sectionName);
                };
            });

            selectedLibraryChoices.value = choices;
        },
        async update(item: AppConfig) {
            const { data } = await api.put<AppConfig>("/api/config", item);
            appConfig.value = data || undefined;
        },
    };

    actions.refresh();
    return {
        actions,
        appConfig,
        allLibraryChoices,
        selectedLibraryChoices,
    }
};
