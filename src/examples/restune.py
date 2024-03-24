import os

from tinytune.llmcontext import Message
from tinytune.prompt import prompt_job
from tinytune.gptcontext import GPTContext, GPTMessage, Model
from tinytune.pipeline import Pipeline, PromptJob

context = GPTContext("gpt-4-0125-preview", str(os.getenv("OPENAI_KEY")))

def Callback(content):
    if (content != None):
        print(content, end="")
    else:   
        print()


@prompt_job(id="Setup")
def Setup(id: str, llm: GPTContext):
    try:
        (context.Prompt(GPTMessage("system", 
                            "You're a resume analyzer. Your job is to look at resumes and compare them to a given job description. You're supposed to divide the resume into different sections, and rate the relevance of each section to the job. Only start the analysis once you're provided the job description"))
            .Run(stream=True).Save())

    except Exception as e:
        raise e

@prompt_job(id="Tune")
def Tune(id: str, llm: GPTContext, prevResult: str):
    (context.Prompt(GPTMessage("user", f"here is the resume Rishit Singh rsrishitsingh@gmail.com |  6723381435 |  Vancouver, BC |  https://github.com/rishit-singhEducationShalom Hills International School Gurugram, IndiaHIGH SCHOOL DIPLOMA IN SCIENCE April 2017 – August 2021GPA: 3.2Langara College Vancouver BCASSOCIATES OF SCIENCE IN COMPUTER SCIENCE Jan 2023 – Jan 2025GPA: 3.6ExperienceLangara Computer Science Club Vancouver, BCTECH LEAD January 2023 – Present• Develop and maintain club projects.• Mentor students in programming.• Host workshops on unique topics of different difficulties.Enablesoft ERP Gurugram, IndiaSOFTWARE ENGINEER October 2021 – June 2023• Made a web based AR engine from scratch using WebXR for previewing products from an e-commerce website.• Made a C# based service to dynamically generate mappable textures of rugs their images on the website.• Automated 3D model generation with the Blender API• Wrote ERP services in C#SkillsProgramming: C++, C#, Java, Kotlin, Python, Go, JavaScriptGraphics APIs and Game Engines: OpenGL, SDL, Vulkan, Unity, Godot, Three.js, WebGLDev Ops: Bash/Linux, Docker, Docker-ComposeWeb Backend: ASP.NET Core, DjangoWeb Frontend: HTML/CSS, ReactMath: Linear algebra, Calculus, StatisticsClasses: CPSC1150 Intro To Programming, CPSC1160 Data Structures and Algorithms I, CPSC1181 ObjectProjectsCacoEngine C++, SDLSDL BASED GAME ENGINE WRITTEN IN C++ https://github.com/rishit-singh/CacoEngineWebAR-Abstraction TypeScript, WebXR, Three.jsA WEB BASED GENERAL PURPOSE AR ENGINE. https://github.com/rishit-singh/WebAR-AbstractionRugTextureGenerator C#, OpenCVA C# BASED SERVICE TO DYNAMICALLY GENERATE MAPPABLE TEXTURES FROM IMAGES OF RUGS. https://github.com/Enablesoft-ERP/RugTextureGeneratorRugViewAR-MeshGen Python, Blender APIBLENDER SCRIPTS TO GENERATE 3D MODELS FOR RUGS. https://github.com/Enablesoft-ERP/RugViewAR-MeshGenOpenDatabaseAPI C#API FOR CREATING AND MAINTAINING SQL BASED DATABASE PROGRAMMATICALLY. https://github.com/rishit-singh/OpenDatabaseAPISharpSession C#A C# BASED WEB SESSION MANAGER https://github.com/rishit-singh/SharpSessionCourseView C#, Blazor.NET, PostGRESQLA WEB FRONTEND WITH SEARCH QUERIES FOR A FAST DATABASE CONTAINING INFO ABOUT ALL COURSESOFFERED AT LANGARA IN UPCOMING AND PREVIOUS TERMS. https://github.com/langaracpsc/CourseViewKeyMan C#A GENERAL PURPOSE API KEY MANAGER. https://github.com/rishit-singh/KeyManlangaracpsc-next Typescript, Next.jsWEBSITE FOR LANGARA CS CLUB. https://langaracs.techperegrine-gpt Python, OpenAI APIA PROMPT TUNED GPT BASED CHATBOT FOR LANGARA CS CLUB. https://github.com/langaracpsc/peregrine-gptGit & Github WorkshopA LCS WORKSHOP EXPLAINING HOW TO USE GIT AND GITHUB IN A PROGRAMMING PROJECT.Intro To Programming in PythonA LCS WORKSHOP GIVING A BRIEF INTRODUCTION TO PROGRAMMING CONCEPTS USING THE PROGRAMMINGLANGUAGE PYTHON.Intro To AIA LCS WORKSHOP EXPLAINING THE GENERAL CONCEPTS OF AI AND ITS CURRENT STATE.Intro to ReactA LCS WORKSHOP GIVING A BRIEF INTRODUCTION TO FRONTEND DEVELOPMENT USING REACT.Intro To REST APIsA LCS WORKSHOP EXPLAINING THE WORKING OF THE REST ARCHITECTURE AND ITS USES IN WEB DEVELOPMENT.ALONG WITH A BRIEF INTRODUCTION TO THE OPENAI API AS AN EXAMPLE.Code CollaborationA LCS WORKSHOP DONE BEFORE THE LANGARA HACKS HACKATHON EVENT TO HELP PEOPLE SETUP THEIR PROJECTSAND COLLABORATE WITH THEIR HACKATHON TEAMS USING TOOLS LIKE GIT.. "))
        .Prompt(GPTMessage("user", """Here's the job description About The Job
                           
As a leader in cloud communications, Line2 is on a mission to provide “everywhere workers” with the means to manage their business communications from anywhere and on any device. Our line of products make it easy to have productive business communication over calls, conferencing, and text messaging.

Line2 is searching for a talented Senior Software Engineer with an exceptional commitment to excellence to join its global engineering team. You will be an integral member of the team, collaborating with diverse and talented team members to help generate value for our customers through platform maintenance and enhancements.

What You’ll Do

Participate in the creation and curation of an evolving team culture
Participate in product reviews and team meetings, providing technical insight. Help scope, estimate, and prioritize between competing priorities.
Work cross-functionally to build new services, features, applications, tools and data models to operate our workflows at scale.
Evaluate new technologies and approaches to streamline and improve every facet of our SDLC.
Regularly learn new systems and tools as the Communications platform and ecosystem evolves.
Design and implement new features and enhancements to existing products.
Participate in the maintenance and troubleshooting of existing applications.
Participate in our on-call rotation and contribute to incident reviews.

Required Experience

5+ years of .NET application development experience
3+ years of experience developing web applications using ASP.NET, with experience using MVC
3+ years developing Secure Applications on-prem and in the cloud. AWS Preferred.
3+ years of .NET Core application development experience
Microsoft SQL Server with a solid understanding of T-SQL programming
Good understanding of various cloud and application resiliency patterns
Good knowledge of OAuth
Good knowledge of AWS
Good knowledge of Entity Framework
Good knowledge of RESTful and WCF web services
Good knowledge of agile principles and experience using scrum methodology
Experience operating and enhancing scalable, fault-tolerant, distributed systems
Refactoring and applying software design patterns to improve and optimize code
Experience developing microservice based distributed systems with high availability, throughput, fault tolerance, and performance.
Worked with GitHub, Github Actions, AWS Code Deploy

Target Salary is $140-$200K

About Moz Group

The Moz Group, a subsidiary of Ziff Davis, Inc (NASDAQ: ZD), is a leading provider of marketing technology solutions primarily for small and medium-sized enterprises, consisting of a portfolio of brands across digital media and cloud services. Our SEO brands include Moz and STAT, Email Marketing brands include Campaigner, iContact, Kickbox, and SMTP, and finally our Communications brands are made up of Line2 and eVoice.

The Moz Group is committed to building diverse teams where people of all identities and backgrounds are welcome, included, and respected. We work to help close the gender gap in tech, and to actively recruit people from other underrepresented groups. We strongly encourage women, gender diverse people, and minority candidates to apply.

Our parent company, Ziff Davis, has once again achieved a perfect score of 100 in the Human Rights Campaign (HRC) Foundation's 2023 Corporate Equality Index (CEI). The CEI is a vital benchmarking tool that evaluates corporate policies and practices, and our consistent top score demonstrates our ongoing dedication to maintaining a diverse and inclusive work environment for all.
Return every section in form of JSON.
""")).Run(stream=True).Save())

context.OnGenerateCallback = Callback

pipeline: Pipeline[GPTMessage] = Pipeline[GPTMessage](context)

pipeline.AddJob(Setup) 
pipeline.AddJob(Tune)
pipeline.AddJob(pipeline)

pipeline.Run()
