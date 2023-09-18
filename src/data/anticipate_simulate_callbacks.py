import src.data.app_utils as app_utils
from dash import html, Input, Output
from notebooks import simulate_utils


def register_callbacks(app):
    categories_skills = app_utils.get_categories_skills()

    @app.callback(
        Output('mode-content', 'children'),
        Input('toggle-switch', 'value')
    )
    def update_content(value):
        """
        Update the content of the main section based on the toggle switch value.

        Args:
            value (bool): The value of the toggle switch.

        Returns:
            html.Div or plotly.graph_objs: The updated content for the main section.
        """
        if value:
            return app_utils.create_simulate_skills_content()
        else:
            return app_utils.create_probability_chart()

    @app.callback(
        Output("selected-skills-output", "children"),
        [Input({"type": "skill-checkbox", "category": category}, "value")
         for category in categories_skills.keys()]
    )
    def update_selected_skills(*selected_skills):
        """
        Update the displayed selected skills based on user's checkbox selections.

        Args:
            *selected_skills: Values of selected skills checkboxes.

        Returns:
            list: The updated content for the selected skills output.
        """
        selected_skills_dict = {category: skills for category, skills in zip(categories_skills.keys(), selected_skills)}
        return app_utils.create_selected_simulated_skills(selected_skills_dict)

    # @app.callback(
    #     Output("current-target-job", "children"),
    #     [Input("job-radio", "value")] + [Input({"type": "skill-checkbox", "category": category}, "value")
    #                                      for category in categories_skills.keys()]
    # )
    # def update_current_expected_job_dev(target_job, *selected_skills):
    #     """
    #     Update the displayed expected current job and target job.
    #
    #     Args:
    #         target_job: Values of selected target job.
    #         *selected_skills: Values of selected skills checkboxes.
    #
    #
    #     Returns:
    #         list: The updated content for the selected skills output.
    #     """
    #     selected_skills = [skill for skills in selected_skills for skill in (skills or [])]
    #
    #     if len(selected_skills) > 2 and target_job:
    #         predictions = app_utils.get_jobs_predictions(selected_skills)
    #         current_job = list(predictions.index)[0]
    #         return app_utils.create_current_target_dev(current_job, target_job)
    #     else:
    #         return html.Div(children=[html.H2('Your current and expected job', style={'text-align': 'center'}),
    #                                   'Please select at least 3 skills and one target job predict your current job']), ''

    @app.callback(
        [Output("simulated-skills-output", "children"), Output('loading-output', 'children')],
        [Input("job-radio", "value")] +
        [Input({"type": "skill-checkbox", "category": category}, "value")
         for category in categories_skills.keys()]
    )
    def update_simulated_skills_output(target_jop, *selected_skills):
        """
        Update the simulated skills output based on selected target job and skills checkboxes.

        Args:
            target_jop: Selected target job.
            *selected_skills: Values of selected skills checkboxes.

        Returns:
            tuple: Updated content for the simulated skills output and loading icon.
        """
        selected_skills = [skill for skills in selected_skills for skill in (skills or [])]
        if target_jop and len(selected_skills) > 2:
            simulate_skills_dict = simulate_utils.get_recommended_categories(target_jop, selected_skills)
            simulate_skills_dict = app_utils.get_categories_skills(simulate_skills_dict)
            predictions = app_utils.get_jobs_predictions(selected_skills)
            current_job = list(predictions.index)[0]
            return app_utils.create_selected_simulated_skills(simulate_skills_dict, "Simulated Skills",
                                                              current_job, target_jop), ''
        else:
            return html.Div(children=[html.H2('Simulated skills', style={'text-align': 'center'}),
                                      'Please select at least 3 skills and one target job to simulate skills']), ''

    @app.callback(
        Output("probability-chart", "figure"),
        [Input({"type": "skill-checkbox", "category": category}, "value")
         for category in categories_skills.keys()]
    )
    def update_chart(*selected_skills):
        """
        Update the probability chart based on selected skills checkboxes.

        Args:
            *selected_skills: Values of selected skills checkboxes.

        Returns:
            plotly.graph_objs: The updated figure for the probability chart.
        """
        selected_skills_count = sum(len(skills) if skills else 0 for skills in selected_skills)

        if selected_skills_count < 3:
            return {}

        if selected_skills_count > 30:
            return {}

        if all(skill_list is None for skill_list in selected_skills):
            return {}

        selected_skills = [skill for skills in selected_skills for skill in (skills or [])]

        if selected_skills:
            predictions = app_utils.get_jobs_predictions(selected_skills)
            fig = app_utils.plot_predictions_jobs(predictions, threshold=10)
            return fig
        else:
            return {}

    @app.callback(
        Output("message-div", "children"),
        [Input({"type": "skill-checkbox", "category": category}, "value")
         for category in categories_skills.keys()]
    )
    def update_message(*selected_skills):
        """
        Update the message displayed based on selected skills checkboxes.

        Args:
            *selected_skills: Values of selected skills checkboxes.

        Returns:
            str: The updated message text.
        """
        selected_skills_count = sum(len(skills) if skills else 0 for skills in selected_skills)

        if selected_skills_count < 3:
            return "Please select at least 3 skills to generate the figure."

        if selected_skills_count > 30:
            return "Selected skills are more than the threshold of 30."

        return ""
